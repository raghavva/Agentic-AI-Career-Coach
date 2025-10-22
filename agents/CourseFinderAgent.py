# agents/CourseFinderAgent.py
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from textwrap import dedent
from agents.tools.course_website_crawler import crawl_course_websites
from urllib.parse import quote_plus
import json
from typing import List
from agents.tools import async_course_crawler


# class CourseFinderAgent:
#     def __init__(self):
#         self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
        
#     def _generate_course_urls(self, skill: str) -> List[str]:
#         """Generate course search URLs for a specific skill"""
#         q = quote_plus(skill)
#         return [
#             f"https://www.coursera.org/search?query={q}",
#             f"https://www.udemy.com/courses/search/?q={q}",
#             #f"https://www.edx.org/search?q={q}",
#             #f"https://www.pluralsight.com/search?q={q}",
#             #f"https://www.linkedin.com/learning/search?keywords={q}"
#         ]
        
#     def create_course_discovery_agent(self):
#         return Agent(
#             role="Educational Course Discovery Specialist",
#             goal="Find and evaluate online courses for skill development",
#             backstory="""You are an expert educational consultant who specializes in finding 
#             high-quality online courses across multiple platforms like Coursera, Udemy, and edX.""",
#             tools=[crawl_course_websites],
#             verbose=True,
#             llm=self.llm,
#             allow_delegation=False
#         )
    
#     def create_course_search_task(self, agent, missing_skills):
#         # Generate URLs for top 2 skills to avoid too many requests
#         all_urls = []
#         skills_to_search = missing_skills[:2]
        
#         for skill in skills_to_search:
#             urls = self._generate_course_urls(skill)
#             all_urls.extend(urls[:2])  # Limit to 2 platforms per skill
        
#         return Task(
#             description=f"""
#             Find courses for these missing skills: {missing_skills}
            
#             Use the crawl_course_websites tool with these URLs: {all_urls}
            
#             Extract course information:
#             - Course titles and descriptions
#             - Platform (Coursera, Udemy, etc.)
#             - Ratings and reviews
#             - Duration and pricing
#             - Instructor information
#             - Course URL (very Important)
            
#             Analyze and rank courses by:
#             - Relevance to missing skills
#             - Course quality indicators
#             - Value for money
#             - Practical applicability
            
#             Return top 20 courses as JSON array with detailed information.
#             """,
#             agent=agent,
#             expected_output="JSON array of top 20 course objects with rankings"
#         )
    
#     def run(self, missing_skills):
#         agent = self.create_course_discovery_agent()
#         task = self.create_course_search_task(agent, missing_skills)
        
#         crew = Crew(
#             agents=[agent],
#             tasks=[task],
#             verbose=True
#         )
        
#         result = crew.kickoff()
        
#         # Parse result - handle both string and CrewAI result objects
#         try:
#             if hasattr(result, 'raw'):
#                 # CrewAI result object
#                 result_text = result.raw
#             elif isinstance(result, str):
#                 result_text = result
#             else:
#                 result_text = str(result)
            
#             # Try to parse as JSON
#             courses = json.loads(result_text)
#             return courses if isinstance(courses, list) else []
            
#         except Exception as e:
#             print(f"Error parsing courses: {e}")
#             return []


class CourseFinderAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
        
    def _generate_course_urls(self, skill: str) -> List[str]:
        """Generate course search URLs for a specific skill"""
        q = quote_plus(skill)
        return [
            f"https://www.coursera.org/search?query={q}",
            f"https://www.udemy.com/courses/search/?q={q}",
            f"https://www.edx.org/search?q={q}",
        ]
        
    def create_course_discovery_agent(self):
        return Agent(
            role="Educational Course Discovery Specialist",
            goal="Find and evaluate online courses for skill development",
            backstory="""You are an expert educational consultant who specializes in finding 
            high-quality online courses across multiple platforms like Coursera, Udemy, and edX.""",
            tools=[async_course_crawler.crawl_courses_async],  # Use the async tool
            verbose=True,
            llm=self.llm,
            allow_delegation=False
        )
    
    def create_course_search_task(self, agent, missing_skills):
        # Generate URLs for all skills but limit platforms
        all_urls = []
        for skill in missing_skills[:2]:  # Limit to 2 skills
            urls = self._generate_course_urls(skill)
            all_urls.extend(urls[:2])  # Only 2 platforms per skill
        
        return Task(
            description=f"""
            Find courses for these missing skills: {missing_skills}
            
            Use the crawl_courses_async tool with these URLs: {all_urls}
            
            Extract course information:
            - Course titles and descriptions
            - Platform (Coursera, Udemy, etc.)
            - Ratings and reviews
            - Duration and pricing
            - Instructor information
            - Course URL (very Important)
            
            IMPORTANT: Return only top 10 courses as JSON array with detailed information.
            Focus on the most relevant and highest-rated courses.
            """,
            agent=agent,
            expected_output="JSON array of top 10 course objects with rankings"
        )

    def run(self, missing_skills):
        agent = self.create_course_discovery_agent()
        task = self.create_course_search_task(agent, missing_skills)
        
        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=True
        )
        
        result = crew.kickoff()
        
        # Parse result - handle both string and CrewAI result objects
        try:
            if hasattr(result, 'raw'):
                # CrewAI result object
                result_text = result.raw
            elif isinstance(result, str):
                result_text = result
            else:
                result_text = str(result)
            
            # Try to parse as JSON
            courses = json.loads(result_text)
            return courses if isinstance(courses, list) else []
            
        except Exception as e:
            print(f"Error parsing courses: {e}")
            return []