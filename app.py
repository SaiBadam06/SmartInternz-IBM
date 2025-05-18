import streamlit as st
import os
import importlib.util
from database import initialize_db
from ai_engine import load_ai_models

# Page configuration
st.set_page_config(
    page_title="SmartLearn",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide Streamlit's native pages from the UI and rename to "SmartLearn"
st.markdown("""
<style>
    /* Completely hide the page menu in sidebar */
    header[data-testid="stHeader"] {
        display: none;
    }
    
    /* Hide the page navigation in sidebar */
    [data-testid="stSidebarNav"] {
        display: none;
    }
    
    /* Make sure no default navigation is shown */
    .stApp > header {
        display: none;
    }
    
    /* Custom styling for the app */
    .main .block-container {
        padding-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

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

# Import page modules dynamically to avoid displaying in UI
pages = {}
for module_name in ["dashboard", "courses", "assessments", "community", "qa", "todo"]:
    module_path = f"pages/{module_name}.py"
    spec = importlib.util.spec_from_file_location(f"pages.{module_name}", module_path)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        pages[module_name] = module

# Sidebar navigation
st.sidebar.title("SmartLearn")

# Display SVG logo
st.sidebar.markdown("""
<div style="text-align: center; margin-bottom: 20px;">
    <svg width="150" height="150" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
        <circle cx="100" cy="100" r="80" fill="#4B89DC" />
        <text x="100" y="90" font-family="Arial" font-size="20" text-anchor="middle" fill="white">SmartLearn</text>
        <path d="M50,110 L150,110" stroke="white" stroke-width="3" />
        <path d="M70,80 L130,80" stroke="white" stroke-width="2" />
        <path d="M60,120 L140,120" stroke="white" stroke-width="2" />
        <circle cx="70" cy="95" r="10" fill="white" />
        <circle cx="130" cy="95" r="10" fill="white" />
        <path d="M85,130 C95,140 105,140 115,130" stroke="white" stroke-width="2" fill="none" />
    </svg>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown(f"Welcome, **{st.session_state.username}**!")
st.sidebar.divider()

# Display current learning material if set
if "current_material" in st.session_state and st.session_state["current_material"]:
    material = st.session_state["current_material"]
    st.sidebar.markdown("""
    <div style="background-color:#f0f2f6; padding:10px; border-radius:5px; margin-bottom:10px;">
        <h4 style="margin:0 0 5px 0;">Currently Learning</h4>
        <p style="font-weight:bold; margin:0 0 5px 0;">📚 {}</p>
        <p style="font-size:0.8em; margin:0;">{}</p>
    </div>
    """.format(
        material.get("title", "Unknown"),
        material.get("category", "")
    ), unsafe_allow_html=True)
    
    if st.sidebar.button("Clear Current Material"):
        st.session_state.pop("current_material", None)
        st.rerun()

st.sidebar.divider()

# Main navigation
nav_options = {
    "Dashboard": "📊",
    "Courses & Materials": "📚",
    "Assessments": "📝",
    "Task Planner": "📋",
    "Community": "👥",
    "Q&A": "❓"
}

# Check if navigation selection was set programmatically
if "nav_selection" in st.session_state:
    selection = st.session_state.pop("nav_selection")
else:
    selection = st.sidebar.radio(
        "Navigation",
        list(nav_options.keys()),
        format_func=lambda x: f"{nav_options[x]} {x}"
    )

# Display the selected page
if selection == "Dashboard":
    pages["dashboard"].show_dashboard(db)
    
elif selection == "Courses & Materials":
    pages["courses"].show_courses(db, ai_models)
    
elif selection == "Assessments":
    pages["assessments"].show_assessments(db, ai_models)
    
elif selection == "Task Planner":
    pages["todo"].show_todo(db)
    
elif selection == "Community":
    pages["community"].show_community(db)
    
elif selection == "Q&A":
    pages["qa"].show_qa(db, ai_models)

# Footer
st.sidebar.divider()
st.sidebar.caption("© 2025 SmartLearn. Powered by IBM Granite LLM")
