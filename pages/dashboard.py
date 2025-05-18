import streamlit as st
import pandas as pd
import numpy as np
from pages.utils import display_progress_chart, display_score_chart, display_summary_metrics, display_radar_chart
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
    
    # Create a more organized dashboard layout with tabs
    tab1, tab2, tab3 = st.tabs(["Overview", "Progress", "Skills"])
    
    with tab1:
        # Display summary metrics
        st.subheader("Learning Overview")
        display_summary_metrics(stats)
        
        # Get course recommendations for the user
        st.subheader("Recommended Courses")
        recommended_courses = get_course_recommendations(db, user_id)
        
        if recommended_courses:
            course_cols = st.columns(min(3, len(recommended_courses)))
            for i, (col, course) in enumerate(zip(course_cols, recommended_courses[:3])):
                with col:
                    st.markdown(f"**{course['title']}**")
                    st.caption(f"{course['category']} | {course['difficulty'].capitalize()}")
                    st.button("Enroll", key=f"overview_enroll_{i}")
        else:
            st.info("Complete more courses to get personalized recommendations.")
    
    with tab2:
        # Display progress charts in a cleaner format
        st.subheader("Your Learning Progress")
        
        # Progress chart
        display_progress_chart(stats["progress_data"])
        
        # Quiz scores chart
        st.subheader("Recent Assessment Results")
        display_score_chart(stats["quiz_data"])
        
        # Display learning streak
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div style="background-color:#f0f2f6; padding:20px; border-radius:10px; text-align:center;">
                <h3 style="margin:0;">🔥 5 days</h3>
                <p>Learning streak</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="background-color:#f0f2f6; padding:20px; border-radius:10px; text-align:center;">
                <h3 style="margin:0;">8 hours</h3>
                <p>Total learning time</p>
            </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        # Display skill assessment with improved layout
        st.subheader("Skill Assessment")
        
        # Sample skill data (in a real implementation, this would come from the database)
        skills_data = pd.DataFrame({
            "skill": ["Python", "Data Science", "Mathematics", "Problem Solving", "Communication"],
            "level": [75, 60, 85, 70, 80]
        })
        
        display_radar_chart(skills_data)
        
        # Display skill breakdown
        st.subheader("Skill Breakdown")
        skill_cols = st.columns(3)
        for i, (skill, level) in enumerate(zip(skills_data["skill"], skills_data["level"])):
            with skill_cols[i % 3]:
                st.markdown(f"**{skill}**")
                st.progress(level/100)
                st.caption(f"{level}% Proficiency")
    
    # Add tasks section to the right sidebar
    st.sidebar.subheader("Today's Tasks")
    if tasks_today:
        for i, task in enumerate(tasks_today):
            with st.sidebar.container():
                priority_color = {
                    "Low": "blue",
                    "Medium": "orange",
                    "High": "red"
                }.get(task.get("priority", "Medium"), "gray")
                
                st.sidebar.markdown(
                    f"<div style='display:flex;align-items:center;'>"
                    f"<span style='color:{priority_color};font-weight:bold;margin-right:10px;'>●</span>"
                    f"<span style='font-weight:bold;'>{task.get('name', 'Untitled Task')}</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )
                st.sidebar.caption(f"{task.get('task_type', 'Task')} • {task.get('time_estimate', 0)} mins")
                
                # Quick complete button
                if st.sidebar.button("✓ Complete", key=f"quick_complete_{i}"):
                    try:
                        db["user_tasks"].update_one(
                            {"_id": task["_id"]},
                            {"$set": {"completed": True}}
                        )
                        st.toast("Task completed!", icon="✅")
                        st.rerun()
                    except Exception as e:
                        st.toast("Could not update task status", icon="⚠️")
                
                st.sidebar.divider()
        
        st.sidebar.markdown("[View All Tasks](/?selection=Task+Planner)")
    else:
        st.sidebar.info("No tasks scheduled for today")
        if st.sidebar.button("+ Add Tasks"):
            st.session_state["nav_selection"] = "Task Planner"
            st.rerun()
        
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
    
    # Already moved personalized recommendations to the Overview tab
