# fastapi_app.py
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Any, Dict, Optional
from utils.cache_manager import cache_manager
import time
from functools import wraps

from utils.pdf_parser import extract_text_from_pdf
from agents.ResumeSkillExtractorAgent import ResumeSkillExtractorAgent
from agents.CareerGoalAnalyzerAgent import CareerGoalAnalyzerAgent
from agents.CourseFinderAgent import CourseFinderAgent
from agents.EvaluatorAgent import EvaluatorAgent

app = FastAPI(title="Agentic AI Career Coach API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten for prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeResponse(BaseModel):
    career_goal: str
    student_skills: List[str]
    ideal_skills: List[str]
    missing_skills: List[str]
    courses_found: int
    top_5_courses: List[Dict[str, Any]]

def _select_top_courses(recommendations: Any, courses: Optional[List[Dict]] = None) -> List[Dict]:
    # Try evaluator output first
    if isinstance(recommendations, dict):
        if "top_courses" in recommendations and isinstance(recommendations["top_courses"], list):
            return recommendations["top_courses"][:5]
        if "courses" in recommendations and isinstance(recommendations["courses"], list):
            return recommendations["courses"][:5]
    if isinstance(recommendations, list):
        return recommendations[:5]
    # Fallback to raw courses
    if courses:
        return courses[:5]
    return []

@app.get("/health")
def health():
    return {"status": "ok"}

def track_performance(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        
        print(f"{func.__name__} took {end_time - start_time:.2f} seconds")
        return result
    return wrapper

@app.post("/analyze", response_model=AnalyzeResponse)
@track_performance
async def analyze_resume(
    career_goal: str = Form(...),
    resume: UploadFile = File(...)
):
    try:
        # 1) Extract resume text
        resume_bytes = await resume.read()
        import io
        resume_text = extract_text_from_pdf(io.BytesIO(resume_bytes))

        # 2) Run agents
        resume_agent = ResumeSkillExtractorAgent()
        student_skills = resume_agent.run(resume_text) or []

        goal_agent = CareerGoalAnalyzerAgent()
        ideal_skills = goal_agent.run(career_goal) or []

        # 3) Compute missing skills
        missing_skills = [s for s in ideal_skills if s not in student_skills]

        # 4) Check cache first
        cached_data = cache_manager.get_cached_courses(career_goal, missing_skills)
        
        if cached_data:
            print(f"Cache hit for {career_goal}")
            courses = cached_data['courses']
            recommendations = cached_data['recommendations']
        else:
            print(f"Cache miss for {career_goal}, generating new data")
            # 5) Find courses
            course_finder = CourseFinderAgent()
            courses = course_finder.run(missing_skills) or []

            # 6) Evaluate recommendations
            evaluator = EvaluatorAgent()
            recommendations = evaluator.run(missing_skills, courses)
            
            # 7) Cache the results
            cache_manager.set_cached_courses(career_goal, missing_skills, courses, recommendations)

        # 8) Pick top 5 courses
        top_5 = _select_top_courses(recommendations, courses)

        return AnalyzeResponse(
            career_goal=career_goal,
            student_skills=student_skills,
            ideal_skills=ideal_skills,
            missing_skills=missing_skills,
            courses_found=len(courses),
            top_5_courses=top_5
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Add cache management endpoints
@app.post("/cache/clear")
async def clear_cache(career_goal: str = None):
    cache_manager.invalidate_cache(career_goal)
    return {"message": "Cache cleared"}

@app.get("/cache/stats")
async def cache_stats():
    if hasattr(cache_manager, 'redis_client'):
        info = cache_manager.redis_client.info('memory')
        return {
            "cache_type": "Redis",
            "memory_usage": info.get('used_memory_human'),
            "keys": cache_manager.redis_client.dbsize()
        }
    else:
        return {
            "cache_type": "In-Memory",
            "cached_entries": len(cache_manager.cache)
        }