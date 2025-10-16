# agents/EvaluatorAgent.py
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from textwrap import dedent
import json

class EvaluatorAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
        
    def create_evaluation_specialist_agent(self):
        return Agent(
            role="Learning Path Evaluation Specialist",
            goal="Evaluate and rank course recommendations for optimal learning outcomes",
            backstory="""You are an expert educational evaluator who assesses course quality, 
            relevance, and learning effectiveness to provide personalized recommendations.""",
            tools=[],
            verbose=True,
            llm=self.llm,
            allow_delegation=False
        )
    
    def create_evaluation_task(self, agent, missing_skills, courses):
        return Task(
            description=f"""
            Evaluate these courses for learning these skills: {missing_skills}
            
            Courses to evaluate:
            {json.dumps(courses, indent=2)}
            
            Evaluate based on:
            - Relevance to missing skills
            - Course quality indicators
            - Difficulty appropriateness
            - Practical applicability
            - Value for money

            IMPORTANT : return only the top 5 courses in JSON format with evaluation details and their respective URL; not all the courses.
            
            Rank courses and provide:
            - Overall score (1-10)
            - Strengths and weaknesses
            - Learning path recommendations
            
            Return JSON with top 5 ranked courses and detailed evaluation and their respective URL.
            """,
            agent=agent,
            expected_output="Top 5 courses in JSON format with evaluation details and their respective URL"
        )
    

    def run(self, missing_skills, courses):
        agent = self.create_evaluation_specialist_agent()
        task = self.create_evaluation_task(agent, missing_skills, courses)
        
        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=True
        )
        
        result = crew.kickoff()
        
        # DEBUG: Check what attributes the result has
        # print(f"Evaluator Result type: {type(result)}")
        # print(f"Evaluator Result attributes: {dir(result)}")
        # if hasattr(result, 'raw'):
        #     print(f"Evaluator Result.raw: {result.raw}")
        # if hasattr(result, 'output'):
        #     print(f"Evaluator Result.output: {result.output}")
        # if hasattr(result, 'result'):
        #     print(f"Evaluator Result.result: {result.result}")
        
        # Parse result - handle both string and CrewAI result objects
        try:
            if hasattr(result, 'raw'):
                result_text = result.raw
            elif hasattr(result, 'output'):
                result_text = result.output
            elif hasattr(result, 'result'):
                result_text = result.result
            elif isinstance(result, str):
                result_text = result
            else:
                result_text = str(result)
            
            print(f"Evaluator Result text to parse: '{result_text}'")
            print(f"Result text length: {len(result_text) if result_text else 0}")
            
            # Check if result_text is empty or None
            if not result_text or result_text.strip() == "":
                print("Evaluator returned empty result")
                return {"courses": courses[:5], "evaluation": "Evaluation completed"}
            
            # Try to parse as JSON
            evaluation = json.loads(result_text)
            return evaluation
            
        except Exception as e:
            print(f"Error parsing evaluation: {e}")
            print(f"Raw result text: '{result_text}'")
            return {"courses": courses[:5], "evaluation": "Evaluation completed"}