# fastapi_app.py
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Any, Dict, Optional

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

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_resume(
    career_goal: str = Form(...),
    resume: UploadFile = File(...)
):
    try:
        # 1) Extract resume text
        resume_bytes = await resume.read()
        # extract_text_from_pdf accepts a file-like object in your Streamlit code; do the same here
        import io
        resume_text = extract_text_from_pdf(io.BytesIO(resume_bytes))

        # 2) Run agents
        resume_agent = ResumeSkillExtractorAgent()
        student_skills = resume_agent.run(resume_text) or []

        goal_agent = CareerGoalAnalyzerAgent()
        ideal_skills = goal_agent.run(career_goal) or []

        # 3) Compute missing skills
        missing_skills = [s for s in ideal_skills if s not in student_skills]

        # 4) Find courses
        course_finder = CourseFinderAgent()
        courses = course_finder.run(missing_skills) or []

        # 5) Evaluate recommendations
        evaluator = EvaluatorAgent()
        recommendations = evaluator.run(missing_skills, courses)

        # 6) Pick top 5 courses with robust parsing
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