# agents/tools/job_website_crawler.py
import asyncio
import threading
import queue
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, LLMConfig, BrowserConfig, CacheMode, LLMExtractionStrategy
from crewai.tools.base_tool import tool
from typing import Dict, List
import json
import os
from urllib.parse import quote_plus

@tool
def crawl_job_websites(job_urls: List[str],career_goal: str) -> str:
    """Crawl job websites to find skill requirements for a specific career goal"""
    try:
        
        # Schema for job posting extraction
        schema = {
            "job_titles": "list of job titles found",
            "required_skills": "list of technical skills mentioned",
            "soft_skills": "list of soft skills mentioned", 
            "experience_level": "experience level required",
            "education_requirements": "education requirements mentioned"
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
                        instruction=f"""Extract job requirements for "{career_goal}" positions. 
                        Focus on skills, experience levels, and qualifications mentioned in job postings.""",
                        max_scroll_steps=5
                    ),
                )
                
                all_results = []
                async with AsyncWebCrawler(config=browser_config) as crawler:
                    for url in job_urls:
                        try:
                            result = await crawler.arun(url=url, config=crawler_config)
                            if result.extracted_content:
                                all_results.append({
                                    "url": url,
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
        return f"Error crawling job websites: {str(e)}"