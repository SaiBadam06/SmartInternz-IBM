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
    
    # Get the current user ID
    user_id = st.session_state.get("user_id", "demo_student_id")
    
    # Show currently active learning material if available
    if "current_material" in st.session_state and st.session_state["current_material"]:
        material = st.session_state["current_material"]
        with st.container():
            st.subheader("Currently Learning")
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"### 📚 {material.get('title', 'Unknown')}")
                st.markdown(f"**Category**: {material.get('category', 'General')}")
                
                if material.get('source'):
                    st.markdown(f"**Source**: [Open Link]({material.get('source')})")
                elif material.get('content'):
                    with st.expander("View Content"):
                        st.markdown(material.get('content', ''))
            
            with col2:
                if st.button("Mark as Complete"):
                    st.session_state.pop("current_material", None)
                    st.toast("Material marked as complete!", icon="🎉")
                    st.rerun()
            
            st.divider()
    
    # Get today's tasks for display on dashboard
    tasks_today = []
    tasks_collection = None
    try:
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        tasks_collection = db["user_tasks"]
        tasks_today = list(tasks_collection.find({
            "user_id": user_id,
            "date": today,
            "completed": False
        }))
    except Exception as e:
        st.warning("Task information could not be loaded")
        
    # Get learning statistics for the current user
    stats = get_learning_stats(db, user_id)
    
    # Create main dashboard layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Display summary metrics
        st.subheader("Learning Overview")
        display_summary_metrics(stats)
        
        # Display progress and score charts
        display_progress_chart(stats["progress_data"])
        display_score_chart(stats["quiz_data"])
        
        # Display skill assessment
        st.subheader("Skill Assessment")
        
        # Sample skill data (in a real implementation, this would come from the database)
        skills_data = pd.DataFrame({
            "skill": ["Python", "Data Science", "Mathematics", "Problem Solving", "Communication"],
            "level": [75, 60, 85, 70, 80]
        })
        
        display_radar_chart(skills_data)
    
    with col2:
        # Display today's tasks
        st.subheader("Today's Tasks")
        if tasks_today:
            for i, task in enumerate(tasks_today):
                with st.container():
                    priority_color = {
                        "Low": "blue",
                        "Medium": "orange",
                        "High": "red"
                    }.get(task.get("priority", "Medium"), "gray")
                    
                    st.markdown(
                        f"<div style='display:flex;align-items:center;'>"
                        f"<span style='color:{priority_color};font-weight:bold;margin-right:10px;'>●</span>"
                        f"<span style='font-weight:bold;'>{task.get('name', 'Untitled Task')}</span>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                    st.caption(f"{task.get('task_type', 'Task')} • {task.get('time_estimate', 0)} mins")
                    
                    # Quick complete button
                    if st.button("✓ Complete", key=f"quick_complete_{i}"):
                        try:
                            db["user_tasks"].update_one(
                                {"_id": task["_id"]},
                                {"$set": {"completed": True}}
                            )
                            st.toast("Task completed!", icon="✅")
                            st.rerun()
                        except Exception as e:
                            st.toast("Could not update task status", icon="⚠️")
                    
                    st.divider()
            
            st.markdown("[View All Tasks](/?selection=Task+Planner)")
        else:
            st.info("No tasks scheduled for today")
            if st.button("+ Add Tasks"):
                st.session_state["nav_selection"] = "Task Planner"
                st.rerun()
        
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
            {"title": "Python Basics Quiz", "due_date": "May 20, 2025", "course": "Python Programming Basics"},
            {"title": "Data Analysis Project", "due_date": "May 25, 2025", "course": "Introduction to Data Science"}
        ]
        
        if deadlines:
            for deadline in deadlines:
                st.markdown(f"**{deadline['title']}** - {deadline['due_date']}")
                st.caption(f"Course: {deadline['course']}")
        else:
            st.info("No upcoming deadlines.")
    
    # Display recommendations
    st.subheader("Personalized Recommendations")
    
    # Get course recommendations for the user
    recommended_courses = get_course_recommendations(db, user_id)
    
    if recommended_courses:
        course_cols = st.columns(min(3, len(recommended_courses)))
        for i, (col, course) in enumerate(zip(course_cols, recommended_courses[:3])):
            with col:
                st.markdown(f"**{course['title']}**")
                st.write(course["description"][:150] + "..." if len(course["description"]) > 150 else course["description"])
                st.caption(f"Category: {course['category']} | Difficulty: {course['difficulty'].capitalize()}")
                
                if st.button("Enroll", key=f"enroll_rec_{i}"):
                    st.toast(f"Enrolled in {course['title']}", icon="✅")
    else:
        st.info("Complete more courses to get personalized recommendations.")
