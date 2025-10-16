# agents/ResumeSkillExtractorAgent.py
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from textwrap import dedent
import json
from agents.tools.analyze_resume_text import analyze_resume_text  # Import the new tool

class ResumeSkillExtractorAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
        
    def create_resume_analyzer_agent(self):
        return Agent(
            role="Resume Analysis Specialist",
            goal="Extract and categorize technical skills from resume text",
            backstory="""You are an expert HR professional and resume analyst who specializes in 
            identifying technical skills from resume content using advanced analysis tools.""",
            tools=[analyze_resume_text],  # Add the tool here
            verbose=True,
            llm=self.llm,
            allow_delegation=False
        )
    
    def create_skill_extraction_task(self, agent, resume_text):
        return Task(
            description=f"""
            Use the analyze_resume_text tool to extract technical skills from this resume:
            
            Resume Text:
            {resume_text}
            
            The tool will return a JSON array of technical skills. Use that result directly.
            """,
            agent=agent,
            expected_output="JSON array of technical skill strings"
        )
    
    def run(self, resume_text):
        agent = self.create_resume_analyzer_agent()
        task = self.create_skill_extraction_task(agent, resume_text)
        
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
            skills = json.loads(result_text)
            if isinstance(skills, list):
                return skills
            else:
                return []
                
        except Exception as e:
            print(f"Error parsing skills: {e}")
            return []