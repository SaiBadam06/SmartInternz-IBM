import streamlit as st
import os
from database import initialize_db
from ai_engine import load_ai_models

# Page configuration
st.set_page_config(
    page_title="EduTutor AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database connection
db_client, db = initialize_db()

# Load AI models
ai_models = load_ai_models()

# Session state initialization
if 'user_id' not in st.session_state:
    # For demo purposes, we'll use a fixed user_id
    st.session_state['user_id'] = "demo_student_id"
    
if 'username' not in st.session_state:
    st.session_state['username'] = "Demo Student"
    
if 'current_course' not in st.session_state:
    st.session_state['current_course'] = None

# Sidebar navigation
st.sidebar.title("EduTutor AI")

# Display SVG logo
st.sidebar.markdown("""
<div style="text-align: center; margin-bottom: 20px;">
    <svg width="150" height="150" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
        <circle cx="100" cy="100" r="80" fill="#4B89DC" />
        <text x="100" y="115" font-family="Arial" font-size="24" text-anchor="middle" fill="white">EduTutor AI</text>
        <path d="M60,80 L140,80 M60,120 L140,120" stroke="white" stroke-width="5" />
        <circle cx="70" cy="100" r="15" fill="white" />
        <circle cx="130" cy="100" r="15" fill="white" />
    </svg>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown(f"Welcome, **{st.session_state.username}**!")
st.sidebar.divider()

# Main navigation
nav_options = {
    "Dashboard": "📊",
    "Courses & Materials": "📚",
    "Assessments": "📝",
    "Community": "👥",
    "Q&A": "❓"
}

selection = st.sidebar.radio(
    "Navigation",
    list(nav_options.keys()),
    format_func=lambda x: f"{nav_options[x]} {x}"
)

# Links to different sections
if selection == "Dashboard":
    from pages.dashboard import show_dashboard
    show_dashboard(db)
    
elif selection == "Courses & Materials":
    from pages.courses import show_courses
    show_courses(db, ai_models)
    
elif selection == "Assessments":
    from pages.assessments import show_assessments
    show_assessments(db, ai_models)
    
elif selection == "Community":
    from pages.community import show_community
    show_community(db)
    
elif selection == "Q&A":
    from pages.qa import show_qa
    show_qa(db, ai_models)

# Footer
st.sidebar.divider()
st.sidebar.caption("© 2023 EduTutor AI. Powered by IBM Granite LLM")
