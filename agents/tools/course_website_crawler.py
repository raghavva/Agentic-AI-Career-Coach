# agents/tools/course_website_crawler.py
import asyncio
import threading
import queue
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, LLMConfig, BrowserConfig, CacheMode, LLMExtractionStrategy
from crewai.tools.base_tool import tool
from typing import Dict, List
import json
import os

@tool
def crawl_course_websites(course_urls: List[str], skill: str) -> str:
    """Crawl course websites to find relevant courses for a specific skill"""
    try:
        # Schema for course extraction
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
        
        # Use threading to avoid event loop conflicts
        result_queue = queue.Queue()
        
        def run_async():
            async def _crawl():
                browser_config = BrowserConfig(headless=True)
                crawler_config = CrawlerRunConfig(
                    cache_mode=CacheMode.BYPASS,
                    word_count_threshold=1,
                    page_timeout=60000,
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
                        max_scroll_steps=5
                    ),
                )
                
                all_results = []
                async with AsyncWebCrawler(config=browser_config) as crawler:
                    for url in course_urls:
                        try:
                            result = await crawler.arun(url=url, config=crawler_config)
                            if result.extracted_content:
                                all_results.append({
                                    "url": url,
                                    "skill": skill,
                                    "data": result.extracted_content
                                })
                        except Exception as e:
                            print(f"Error crawling {url}: {e}")
                            continue
                
                return json.dumps(all_results)
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(_crawl())
                result_queue.put(result)
            finally:
                loop.close()
        
        # Run in separate thread
        thread = threading.Thread(target=run_async)
        thread.start()
        thread.join()
        
        return result_queue.get()
        
    except Exception as e:
        return f"Error crawling course websites: {str(e)}"