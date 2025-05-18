import streamlit as st
from database import get_user_courses
from pages.utils import create_course_card
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
    
    # Initialize form state if not present
    if "material_form_state" not in st.session_state:
        st.session_state.material_form_state = {
            "title": "",
            "source_type": "URL",
            "url": "",
            "text_content": "",
            "category": "Computer Science",
            "difficulty": "intermediate"
        }
    
    # Create a container for the dynamic form
    form_container = st.container()
    
    with form_container:
        # Title input (outside the dynamic part)
        title = st.text_input(
            "Title", 
            value=st.session_state.material_form_state["title"],
            placeholder="Enter the title of your material or course"
        )
        
        # Source type selection
        source_type = st.radio(
            "Source Type", 
            ["URL", "Text Note", "Upload Notes"],
            index=["URL", "Text Note", "Upload Notes"].index(st.session_state.material_form_state["source_type"])
        )
        
        # Update the source type in session state
        st.session_state.material_form_state["source_type"] = source_type
        
        # Dynamic form fields based on source type
        source = ""
        content = ""
        uploaded_file = None
        file_content = None
        file_name = None
        
        if source_type == "URL":
            source = st.text_input(
                "Course/Material URL", 
                value=st.session_state.material_form_state["url"],
                placeholder="https://..."
            )
            st.session_state.material_form_state["url"] = source
            
        elif source_type == "Text Note":
            content = st.text_area(
                "Material Content", 
                value=st.session_state.material_form_state["text_content"],
                height=200, 
                placeholder="Enter your notes or material content here..."
            )
            st.session_state.material_form_state["text_content"] = content
            
        else:  # Upload Notes
            st.markdown("#### Upload your notes file (PDF, DOCX, TXT)")
            uploaded_file = st.file_uploader(
                "Choose a file", 
                type=["pdf", "docx", "txt"], 
                label_visibility="collapsed"
            )
            
            if uploaded_file is not None:
                st.success(f"File selected: {uploaded_file.name}")
                
                # Preview button for text files
                if uploaded_file.name.endswith('.txt'):
                    if st.button("Preview Text Content"):
                        file_bytes = uploaded_file.read()
                        preview_content = file_bytes.decode('utf-8')
                        st.text_area("File Preview", preview_content[:1000] + ("..." if len(preview_content) > 1000 else ""), height=200)
                        # Reset file position
                        uploaded_file.seek(0)
        
        # Category selection
        categories = ["Computer Science", "Data Science", "Mathematics", "Language Learning", "Science", "Other"]
        category = st.selectbox(
            "Category", 
            categories,
            index=categories.index(st.session_state.material_form_state["category"]) if st.session_state.material_form_state["category"] in categories else 0
        )
        st.session_state.material_form_state["category"] = category
        
        # Difficulty selection
        difficulty_options = ["beginner", "intermediate", "advanced"]
        difficulty = st.select_slider(
            "Difficulty", 
            options=difficulty_options, 
            value=st.session_state.material_form_state["difficulty"]
        )
        st.session_state.material_form_state["difficulty"] = difficulty
        
        # Submit button
        if st.button("Add Material"):
            valid_submission = False
            
            if source_type == "URL" and title and source:
                valid_submission = True
            elif source_type == "Text Note" and title and content:
                valid_submission = True
            elif source_type == "Upload Notes" and title and uploaded_file is not None:
                # Process the uploaded file
                try:
                    file_bytes = uploaded_file.read()
                    file_name = uploaded_file.name
                    
                    # For text files, we can read the content
                    if file_name.endswith('.txt'):
                        file_content = file_bytes.decode('utf-8')
                    else:
                        # For binary files like PDF/DOCX, we just note the file name
                        file_content = f"Uploaded file: {file_name}"
                        
                    valid_submission = True
                except Exception as e:
                    st.toast(f"Error processing file: {str(e)}", icon="⚠️")
            
            if valid_submission:
                # Save the material to the database
                materials_collection = db["user_materials"]
                
                material = {
                    "user_id": user_id,
                    "title": title,
                    "source_type": source_type,
                    "source": source,
                    "content": content if source_type != "Upload Notes" else file_content,
                    "file_name": file_name if source_type == "Upload Notes" else None,
                    "category": category,
                    "difficulty": difficulty,
                    "created_at": datetime.now()
                }
                
                materials_collection.insert_one(material)
                st.toast("Material added successfully!", icon="✅")
                
                # Reset the form
                st.session_state.material_form_state = {
                    "title": "",
                    "source_type": "URL",
                    "url": "",
                    "text_content": "",
                    "category": "Computer Science",
                    "difficulty": "intermediate"
                }
                st.rerun()
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
