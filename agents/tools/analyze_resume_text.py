from crewai.tools.base_tool import tool
from typing import Dict, List
import json
import os
from langchain_openai import ChatOpenAI


@tool
def analyze_resume_text(resume_text: str) -> str:
    """Analyze resume text and extract technical skills using LLM."""
    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
        
        prompt = f"""
        Analyze this resume text and extract ONLY technical skills. Return a JSON array of skill strings.
        
        Resume Text:
        {resume_text}
        
        Extract:
        - Programming languages (Python, Java, JavaScript, etc.)
        - Tools and frameworks (React, Django, TensorFlow, etc.)
        - Databases (MySQL, MongoDB, PostgreSQL, etc.)
        - Cloud platforms (AWS, Azure, GCP, etc.)
        - Other technical skills
        
        Return ONLY a JSON array like: ["Python", "React", "AWS", "Docker"]
        """
        
        response = llm.invoke(prompt)
        return response.content
        
    except Exception as e:
        return f"Error analyzing resume: {str(e)}"