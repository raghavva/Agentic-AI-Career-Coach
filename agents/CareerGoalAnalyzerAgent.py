# agents/CareerGoalAnalyzerAgent.py
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from textwrap import dedent
from agents.tools.job_website_crawler import crawl_job_websites
from urllib.parse import quote_plus
import json
from typing import List

class CareerGoalAnalyzerAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
        
    def _generate_job_urls(self, career_goal: str) -> List[str]:
        """Generate job search URLs based on career goal"""
        q = quote_plus(career_goal)
        return [
            f"https://www.indeed.com/jobs?q={q}",
            f"https://www.linkedin.com/jobs/search/?keywords={q}",
            #f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={q}"
        ]
        
    def create_job_market_analyzer_agent(self):
        return Agent(
            role="Job Market Research Specialist",
            goal="Analyze job market requirements for specific career goals by crawling job websites",
            backstory="""You are an expert career counselor and job market analyst who researches 
            current job requirements and skill demands across industries by analyzing real job postings.""",
            tools=[crawl_job_websites],
            verbose=True,
            llm=self.llm,
            allow_delegation=False
        )
    
    def create_market_research_task(self, agent, career_goal):
        job_urls = self._generate_job_urls(career_goal)
        
        return Task(
            description=f"""
            Research job market requirements for: "{career_goal} and only extract technical skills"
            
            Use the crawl_job_websites tool with these URLs: {job_urls} and only extract technical skills
            
            Extract and analyze:
            - Technical skills (programming languages, tools, frameworks)
            - Experience levels expected
            - Industry-specific knowledge
            
            Return a consolidated JSON array of required skills with frequency counts.
            """,
            agent=agent,
            expected_output="JSON array of required skills with frequency data; return the JSON with top 6 skills with highest frequency" #return skills with highest frequenct top 10
        )
    
    def run(self, career_goal):
        agent = self.create_job_market_analyzer_agent()
        task = self.create_market_research_task(agent, career_goal)
        
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
            skills_data = json.loads(result_text)
            if isinstance(skills_data, list):
                return [skill.get('skill', skill) if isinstance(skill, dict) else skill for skill in skills_data]
            return skills_data
            
        except Exception as e:
            print(f"Error parsing career goal skills: {e}")
            return []