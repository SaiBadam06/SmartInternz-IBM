import streamlit as st
import pandas as pd
import numpy as np
from .utils import display_progress_chart, display_score_chart, display_summary_metrics, display_radar_chart
from database import get_learning_stats, get_course_recommendations

def show_dashboard(db):
    """Display the dashboard page with learning statistics and recommendations"""
    st.title("📊 Dashboard")
    
    # Display welcome message
    st.markdown("""
    ### Welcome to your personalized learning dashboard!
    
    Here you can track your progress, see your recent performance, and get personalized recommendations for your learning journey.
    """)
    
    # Get learning statistics for the current user
    user_id = st.session_state.get("user_id", "demo_student_id")
    stats = get_learning_stats(db, user_id)
    
    # Display summary metrics
    st.subheader("Learning Overview")
    display_summary_metrics(stats)
    
    # Display progress and score charts
    col1, col2 = st.columns(2)
    
    with col1:
        display_progress_chart(stats["progress_data"])
    
    with col2:
        display_score_chart(stats["quiz_data"])
    
    # Display skill assessment
    st.subheader("Skill Assessment")
    
    # Sample skill data (in a real implementation, this would come from the database)
    skills_data = pd.DataFrame({
        "skill": ["Python", "Data Science", "Mathematics", "Problem Solving", "Communication"],
        "level": [75, 60, 85, 70, 80]
    })
    
    display_radar_chart(skills_data)
    
    # Display recommendations
    st.subheader("Personalized Recommendations")
    
    # Get course recommendations for the user
    recommended_courses = get_course_recommendations(db, user_id)
    
    if recommended_courses:
        for course in recommended_courses:
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**{course['title']}**")
                    st.write(course["description"])
                    st.caption(f"Category: {course['category']} | Difficulty: {course['difficulty'].capitalize()}")
                    
                with col2:
                    st.button("Enroll", key=f"enroll_rec_{course['_id']}")
                
                st.markdown("---")
    else:
        st.info("Complete more courses to get personalized recommendations.")
    
    # Display learning streak
    st.subheader("Learning Streak")
    
    # Sample streak data (in a real implementation, this would come from the database)
    streak_days = 5
    
    st.markdown(f"### 🔥 {streak_days} days")
    st.write("Keep up the good work! Consistency is key to learning success.")
    
    # Display upcoming deadlines
    st.subheader("Upcoming Deadlines")
    
    # Sample deadlines (in a real implementation, this would come from the database)
    deadlines = [
        {"title": "Python Basics Quiz", "due_date": "May 20, 2023", "course": "Python Programming Basics"},
        {"title": "Data Analysis Project", "due_date": "May 25, 2023", "course": "Introduction to Data Science"}
    ]
    
    if deadlines:
        for deadline in deadlines:
            st.markdown(f"**{deadline['title']}** - {deadline['due_date']}")
            st.caption(f"Course: {deadline['course']}")
    else:
        st.info("No upcoming deadlines.")
