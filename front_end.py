# main_app.py
import streamlit as st
from agents.ResumeSkillExtractorAgent import ResumeSkillExtractorAgent
from agents.CareerGoalAnalyzerAgent import CareerGoalAnalyzerAgent
from agents.CourseFinderAgent import CourseFinderAgent
from agents.EvaluatorAgent import EvaluatorAgent
from utils.pdf_parser import extract_text_from_pdf
import json

# front_end.py - Update the main workflow
def main():
    st.title("🎓 AI Skill-Gap & Course Recommender")
    st.write("Upload your resume and tell us your career goal — we'll find what skills you're missing and which courses can help you close the gap!")

    uploaded_resume = st.file_uploader("📄 Upload your Resume (PDF)", type=["pdf"])
    career_goal = st.text_input("🎯 Desired Career Goal", placeholder="e.g., Data Scientist, Cloud Engineer, Product Manager")

    if st.button("Find My Learning Path"):
        if uploaded_resume and career_goal:
            # Step 1: Extract skills from resume
            st.info("Extracting your skills from the resume...")
            resume_text = extract_text_from_pdf(uploaded_resume)
            
            resume_agent = ResumeSkillExtractorAgent()
            student_skills = resume_agent.run(resume_text)

            if student_skills:
                st.success(f"✅ Skills extracted: {', '.join(student_skills)}")
            else:
                st.error("❌ No skills extracted from resume!")

            # Step 2: Analyze career goal requirements
            st.info(f"Analyzing skill requirements for '{career_goal}'...")
            goal_agent = CareerGoalAnalyzerAgent()
            ideal_skills = goal_agent.run(career_goal)

            if ideal_skills:
                st.success(f"✅ Required skills: {', '.join(ideal_skills)}")
            else:
                st.error("❌ No skills found for career goal!")

            # Step 3: Find missing skills
            st.info("Comparing and identifying missing skills...")
            missing_skills = [skill for skill in ideal_skills if skill not in student_skills]

            if missing_skills:
                st.write(f"🧩 Missing Skills: {', '.join(missing_skills)}")
            else:
                st.warning("⚠️ No missing skills found - either both lists are empty or student has all required skills")

            # Step 4: Find courses
            st.info("Searching for top-rated courses to close your skill gaps...")
            course_finder = CourseFinderAgent()
            courses = course_finder.run(missing_skills)

            # Step 5: Evaluate recommendations (get top 5)
            st.info("Evaluating course recommendations...")
            evaluator = EvaluatorAgent()
            recommendations = evaluator.run(missing_skills, courses)

            # Display results - Show top 5 courses in expandable view only
            st.subheader("📚 Top 5 Recommended Courses")
            
            # Get the top 5 courses
            top_5_courses = []
            
            if recommendations and isinstance(recommendations, dict):
                if 'top_courses' in recommendations:
                    top_5_courses = recommendations['top_courses'][:5]
                elif 'courses' in recommendations:
                    top_5_courses = recommendations['courses'][:5]
            elif courses:
                top_5_courses = courses[:5]
            
            if top_5_courses:
                st.success(f"✅ Found {len(top_5_courses)} courses")
                
                # Display courses in expandable format only
                for i, course in enumerate(top_5_courses, 1):
                    with st.expander(f"Course {i}: {course.get('course_title', course.get('title', 'Unknown Course'))}"):
                        st.write(f"**Platform:** {course.get('platform', 'N/A')}")
                        st.write(f"**Rating:** {course.get('rating', 'N/A')}")
                        st.write(f"**Duration:** {course.get('duration', 'N/A')}")
                        st.write(f"**Price:** {course.get('price', 'N/A')}")
                        st.write(f"**Description:** {course.get('course_description', course.get('description', 'N/A'))}")
                        st.write(f"**Instructor:** {course.get('instructor', 'N/A')}")
                        
                        course_url = course.get('course_url') or course.get('url') or course.get('link')
                        if course_url:
                            st.write(f"**Course URL:** {course_url}")
                            st.markdown(f"[🔗 Open Course]({course_url})")
                        else:
                            st.warning("⚠️ No course URL found")
            else:
                st.error("❌ No courses found!")

        else:
            st.warning("Please upload a resume and enter your career goal")

if __name__ == "__main__":
    main()