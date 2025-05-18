import streamlit as st
from database import get_user_courses
from .utils import create_course_card
from ai_engine import generate_content, summarize_learning_material
from datetime import datetime

def show_courses(db, ai_models):
    """Display the courses and materials page"""
    st.title("📚 Courses & Materials")
    
    # Get the current user ID
    user_id = st.session_state.get("user_id", "demo_student_id")
    
    # Tabs for My Courses, Explore Courses, and Add Your Material
    tab1, tab2, tab3 = st.tabs(["My Courses", "Explore Courses", "Add Your Material"])
    
    with tab1:
        show_my_courses(db, user_id)
    
    with tab2:
        show_explore_courses(db, user_id)
    
    with tab3:
        show_add_your_material(db, user_id)

def show_my_courses(db, user_id):
    """Show courses that the user is enrolled in"""
    st.header("My Courses")
    
    # Get user's courses
    user_courses = get_user_courses(db, user_id)
    
    if user_courses:
        for course in user_courses:
            # Display course information in a card
            create_course_card(course, is_enrolled=True)
    else:
        st.info("You are not enrolled in any courses yet. Explore courses to get started with your learning journey.")

def show_explore_courses(db, user_id):
    """Show available courses for exploration"""
    st.header("Explore Courses")
    
    # Categories filter
    categories = ["All", "Computer Science", "Data Science", "Mathematics", "Language Learning", "Science"]
    selected_category = st.selectbox("Filter by Category", categories)
    
    # Difficulty filter
    difficulties = ["All", "beginner", "intermediate", "advanced"]
    selected_difficulty = st.selectbox("Filter by Difficulty", difficulties)
    
    # Search box
    search_query = st.text_input("Search Courses", "")
    
    # Query the database for courses
    courses_collection = db["courses"]
    query = {}
    
    if selected_category != "All":
        query["category"] = selected_category
        
    if selected_difficulty != "All":
        query["difficulty"] = selected_difficulty
    
    if search_query:
        query["$or"] = [
            {"title": {"$regex": search_query, "$options": "i"}},
            {"description": {"$regex": search_query, "$options": "i"}}
        ]
    
    # Get user's current courses to exclude them
    user_progress = db["progress"].find({"user_id": user_id})
    enrolled_course_ids = [p["course_id"] for p in user_progress]
    
    if enrolled_course_ids:
        query["_id"] = {"$nin": enrolled_course_ids}
    
    courses = list(courses_collection.find(query))
    
    if courses:
        for course in courses:
            create_course_card(course, is_enrolled=False)
    else:
        st.info("No courses found matching your criteria.")

def show_add_your_material(db, user_id):
    """Show interface for adding user's own learning materials"""
    st.header("Add Your Material")
    
    st.markdown("""
    Add your own learning materials or course links to keep track of your resources in one place.
    """)
    
    # Material form
    with st.form("add_material_form"):
        # Title input
        title = st.text_input("Title", placeholder="Enter the title of your material or course")
        
        # Source input (URL or file)
        source_type = st.radio("Source Type", ["URL", "Text Note"])
        
        if source_type == "URL":
            source = st.text_input("Course/Material URL", placeholder="https://...")
            content = ""
        else:
            source = ""
            content = st.text_area("Material Content", height=200, placeholder="Enter your notes or material content here...")
        
        # Category selection
        categories = ["Computer Science", "Data Science", "Mathematics", "Language Learning", "Science", "Other"]
        category = st.selectbox("Category", categories)
        
        # Difficulty selection
        difficulty_options = ["beginner", "intermediate", "advanced"]
        difficulty = st.select_slider("Difficulty", options=difficulty_options, value="intermediate")
        
        # Submit button
        submitted = st.form_submit_button("Add Material")
        
    if submitted:
        if title and (source or content):
            # Save the material to the database
            materials_collection = db["user_materials"]
            
            material = {
                "user_id": user_id,
                "title": title,
                "source_type": source_type,
                "source": source,
                "content": content,
                "category": category,
                "difficulty": difficulty,
                "created_at": datetime.now()
            }
            
            materials_collection.insert_one(material)
            st.toast("Material added successfully!", icon="✅")
        else:
            st.toast("Please fill in all required fields", icon="⚠️")
    
    # Display saved materials
    st.subheader("My Saved Materials")
    
    # Query the database for saved materials
    materials_collection = db["user_materials"]
    saved_materials = list(materials_collection.find({"user_id": user_id}))
    
    if saved_materials:
        for i, material in enumerate(saved_materials):
            with st.expander(f"{material['title']} ({material['difficulty']})"):
                if material["source_type"] == "URL":
                    st.markdown(f"**URL**: [{material['source']}]({material['source']})")
                    st.markdown(f"**Category**: {material['category']}")
                    
                    # Add a button to mark as current material
                    if st.button("Set as Current Material", key=f"current_{i}"):
                        if "current_material" not in st.session_state:
                            st.session_state["current_material"] = {}
                        
                        st.session_state["current_material"] = {
                            "title": material["title"],
                            "source": material["source"],
                            "category": material["category"],
                            "id": material.get("_id", "")
                        }
                        st.toast(f"Now learning: {material['title']}", icon="📚")
                else:
                    st.markdown(f"**Category**: {material['category']}")
                    st.markdown("**Content**:")
                    st.markdown(material["content"])
                    
                    # Add a button to mark as current material
                    if st.button("Set as Current Material", key=f"current_{i}"):
                        if "current_material" not in st.session_state:
                            st.session_state["current_material"] = {}
                        
                        st.session_state["current_material"] = {
                            "title": material["title"],
                            "content": material["content"][:50] + "...",
                            "category": material["category"],
                            "id": material.get("_id", "")
                        }
                        st.toast(f"Now learning: {material['title']}", icon="📚")
                
                # Option to delete this material
                if st.button("Delete", key=f"delete_{i}"):
                    materials_collection.delete_one({"_id": material["_id"]})
                    st.toast("Material deleted!", icon="🗑️")
                    st.rerun()
    else:
        st.info("You don't have any saved materials yet.")
