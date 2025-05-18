import streamlit as st
from database import get_user_courses
from .utils import create_course_card
from ai_engine import generate_content, summarize_learning_material

def show_courses(db, ai_models):
    """Display the courses and materials page"""
    st.title("📚 Courses & Materials")
    
    # Get the current user ID
    user_id = st.session_state.get("user_id", "demo_student_id")
    
    # Tabs for My Courses, Explore Courses, and Create Custom Material
    tab1, tab2, tab3 = st.tabs(["My Courses", "Explore Courses", "Create Custom Material"])
    
    with tab1:
        show_my_courses(db, user_id)
    
    with tab2:
        show_explore_courses(db, user_id)
    
    with tab3:
        show_create_custom_material(db, ai_models, user_id)

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

def show_create_custom_material(db, ai_models, user_id):
    """Show interface for creating custom learning material"""
    st.header("Create Custom Learning Material")
    
    st.markdown("""
    Use AI to generate custom learning materials on any topic you're interested in.
    Just enter the topic, select the difficulty level, and specify your preferred learning style.
    """)
    
    # Topic input
    topic = st.text_input("Topic", "")
    
    # Difficulty selection
    difficulty_options = ["beginner", "intermediate", "advanced"]
    difficulty = st.select_slider("Difficulty", options=difficulty_options, value="intermediate")
    
    # Learning style selection
    learning_style_options = ["visual", "auditory", "reading/writing", "kinesthetic"]
    learning_style = st.selectbox("Learning Style", learning_style_options)
    
    # Create button
    if st.button("Generate Material"):
        if topic:
            with st.spinner("Generating custom material..."):
                content = generate_content(ai_models, topic, difficulty, learning_style)
                
                # Display the generated content
                st.subheader(f"Custom Material: {topic}")
                st.write(content)
                
                # Generate a summary
                with st.expander("Show Summary"):
                    summary = summarize_learning_material(ai_models, content)
                    st.write(summary)
                
                # Option to save this material
                if st.button("Save to My Materials"):
                    # Save the material to the database
                    materials_collection = db.get("custom_materials", db["custom_materials"])
                    material = {
                        "user_id": user_id,
                        "topic": topic,
                        "difficulty": difficulty,
                        "learning_style": learning_style,
                        "content": content,
                        "summary": summary,
                        "created_at": st.session_state.get("now", None)
                    }
                    materials_collection.insert_one(material)
                    st.success("Material saved to your collection!")
        else:
            st.warning("Please enter a topic.")
    
    # Display saved materials
    st.subheader("My Saved Materials")
    
    # Query the database for saved materials
    materials_collection = db.get("custom_materials", db["custom_materials"])
    saved_materials = list(materials_collection.find({"user_id": user_id}))
    
    if saved_materials:
        for material in saved_materials:
            with st.expander(f"{material['topic']} ({material['difficulty']})"):
                st.write(material["content"])
                
                # Option to delete this material
                if st.button("Delete", key=f"delete_{material.get('_id', 'unknown')}"):
                    materials_collection.delete_one({"_id": material["_id"]})
                    st.success("Material deleted!")
                    st.rerun()
    else:
        st.info("You don't have any saved custom materials yet.")
