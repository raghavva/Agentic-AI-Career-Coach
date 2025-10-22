import asyncio
import aiohttp
import json
from typing import List, Dict, Any
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, LLMConfig, BrowserConfig, CacheMode, LLMExtractionStrategy
import os
from crewai.tools.base_tool import tool

class AsyncCourseCrawler:
    def __init__(self):
        self.semaphore = asyncio.Semaphore(3)  # Limit concurrent requests
        self.timeout = aiohttp.ClientTimeout(total=30)
    

    async def crawl_single_url(self, session: aiohttp.ClientSession, url: str, skill: str) -> Dict[str, Any]:
        """Crawl a single URL asynchronously"""
        async with self.semaphore:  # Limit concurrent requests
            try:
                schema = {
                    "course_titles": "list of course titles found",
                    "course_descriptions": "list of course descriptions",
                    "platforms": "list of course platforms (Coursera, Udemy, etc.)",
                    "ratings": "list of course ratings",
                    "prices": "list of course prices",
                    "durations": "list of course durations",
                    "instructors": "list of instructor names",
                    "course_url": "list of course URLs"
                }
                
                browser_config = BrowserConfig(headless=True)
                crawler_config = CrawlerRunConfig(
                    cache_mode=CacheMode.BYPASS,
                    word_count_threshold=1,
                    page_timeout=30000,  # Reduced timeout
                    extraction_strategy=LLMExtractionStrategy(
                        llm_config=LLMConfig(
                            provider="openai/gpt-4o-mini",
                            api_token=os.getenv("OPENAI_API_KEY")
                        ),
                        schema=schema,
                        extraction_type="schema",
                        instruction=f"""Extract course information for learning "{skill}". 
                        Focus on course titles, descriptions, platforms, ratings, prices, and durations.
                        Make sure to capture the full course URL for each course found.""",
                        max_scroll_steps=2  # Reduced scroll steps
                    ),
                )
                
                async with AsyncWebCrawler(config=browser_config) as crawler:
                    result = await crawler.arun(url=url, config=crawler_config)
                    if result.extracted_content:
                        return {
                            "url": url,
                            "skill": skill,
                            "data": result.extracted_content,
                            "success": True
                        }
                    else:
                        return {"url": url, "skill": skill, "data": None, "success": False}
                        
            except Exception as e:
                print(f"Error crawling {url}: {e}")
                return {"url": url, "skill": skill, "error": str(e), "success": False}
    
    async def crawl_multiple_urls(self, urls: List[str], skill: str) -> List[Dict[str, Any]]:
        """Crawl multiple URLs in parallel"""
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            tasks = [self.crawl_single_url(session, url, skill) for url in urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and failed requests
            successful_results = []
            for result in results:
                if isinstance(result, dict) and result.get('success'):
                    successful_results.append(result)
                elif isinstance(result, Exception):
                    print(f"Task failed with exception: {result}")
            
            return successful_results

# Thread-safe wrapper for the async crawler
import threading
import queue

@tool
def crawl_courses_async(urls: List[str], skill: str) -> str:
    """Thread-safe wrapper for async crawling"""
    result_queue = queue.Queue()
    
    def run_async():
        async def _crawl():
            crawler = AsyncCourseCrawler()
            results = await crawler.crawl_multiple_urls(urls, skill)
            return json.dumps(results)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(_crawl())
            result_queue.put(result)
        except Exception as e:
            result_queue.put(f"Error: {str(e)}")
        finally:
            loop.close()
    
    thread = threading.Thread(target=run_async)
    thread.start()
    thread.join(timeout=120)  # 2-minute timeout
    
    if thread.is_alive():
        return json.dumps({"error": "Crawling timeout"})
    
    try:
        return result_queue.get_nowait()
    except queue.Empty:
        return json.dumps({"error": "No results"})