import streamlit as st
from database import get_user_courses, enroll_in_course, unenroll_from_course, update_user_material
from pages.utils import create_course_card
from ai_engine import generate_content, summarize_learning_material
from datetime import datetime
import webbrowser
import base64
import docx
from docx.shared import Inches
from io import BytesIO

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
            # Create a container for each course
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # Display course information
                    st.subheader(course.get("title", "Untitled Course"))
                    st.write(f"Category: {course.get('category', 'Uncategorized')}")
                    st.write(f"Difficulty: {course.get('difficulty', 'Not specified')}")
                    
                    # Display course materials
                    if "materials" in course:
                        st.write("Course Materials:")
                        for material in course["materials"]:
                            material_type = material.get("type", "Unknown")
                            material_title = material.get("title", "Untitled")
                            
                            if material_type == "pdf":
                                if st.button(f"📄 {material_title}", key=f"pdf_{material['id']}"):
                                    # Handle PDF viewing
                                    pdf_url = material.get("url")
                                    if pdf_url:
                                        webbrowser.open(pdf_url)
                            elif material_type == "url":
                                if st.button(f"🌐 {material_title}", key=f"url_{material['id']}"):
                                    # Open URL in browser
                                    webbrowser.open(material.get("url"))
                            elif material_type == "text":
                                if st.button(f"📝 {material_title}", key=f"text_{material['id']}"):
                                    # Show text content in expander
                                    with st.expander("View Content"):
                                        st.write(material.get("content"))
                
                with col2:
                    # Continue Learning button
                    if st.button("Continue Learning", key=f"continue_{course['_id']}"):
                        # Get the last accessed material or first material
                        materials = course.get("materials", [])
                        if materials:
                            last_material = materials[0]  # For now, just get the first material
                            material_type = last_material.get("type", "")
                            material_url = last_material.get("url", "")
                            
                            if material_type == "pdf" or material_type == "url":
                                webbrowser.open(material_url)
                            elif material_type == "text":
                                st.session_state.current_material = last_material
                                st.rerun()
                    
                    # Unenroll button
                    if st.button("Unenroll", key=f"unenroll_{course['_id']}"):
                        unenroll_from_course(db, user_id, course["_id"])
                        st.rerun()
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
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # Display course information
                    st.subheader(course.get("title", "Untitled Course"))
                    st.write(f"Category: {course.get('category', 'Uncategorized')}")
                    st.write(f"Difficulty: {course.get('difficulty', 'Not specified')}")
                    st.write(course.get("description", "No description available"))
                    
                    # Display available materials
                    if "materials" in course:
                        st.write("Available Materials:")
                        for material in course["materials"]:
                            material_type = material.get("type", "Unknown")
                            material_title = material.get("title", "Untitled")
                            
                            if material_type == "pdf":
                                st.write(f"📄 {material_title}")
                                if st.button("View PDF", key=f"view_pdf_{material['id']}"):
                                    webbrowser.open(material.get("url"))
                            elif material_type == "url":
                                st.write(f"🌐 {material_title}")
                                if st.button("Visit Website", key=f"visit_{material['id']}"):
                                    webbrowser.open(material.get("url"))
                            elif material_type == "text":
                                st.write(f"📝 {material_title}")
                                if st.button("View Content", key=f"view_{material['id']}"):
                                    with st.expander("Material Content"):
                                        st.write(material.get("content"))
                
                with col2:
                    # Enroll button
                    if st.button("Enroll", key=f"enroll_{course['_id']}"):
                        enroll_in_course(db, user_id, course["_id"])
                        st.success("Successfully enrolled in the course!")
                        st.rerun()
                    
                    # Add to Practice Questions button
                    if st.button("Add to Practice Questions", key=f"practice_{course['_id']}"):
                        # Add to user's practice questions
                        practice_collection = db["practice_questions"]
                        practice_collection.insert_one({
                            "user_id": user_id,
                            "course_id": course["_id"],
                            "course_title": course.get("title", "Untitled Course"),
                            "added_at": datetime.now(),
                            "status": "pending"
                        })
                        st.success("Added to practice questions!")
    else:
        st.info("No courses found matching your criteria.")

def show_add_your_material(db, user_id):
    """Show interface for adding user's own learning materials"""
    st.header("Add Your Material")
    
    # Initialize form state if not present
    if "material_form_state" not in st.session_state:
        st.session_state.material_form_state = {
            "title": "",
            "source_type": "URL",
            "url": "",
            "text_content": "",
            "category": "Computer Science",
            "difficulty": "intermediate",
            "highlights": [],
            "images": []
        }
    
    # Create a container for the dynamic form
    form_container = st.container()
    
    with form_container:
        # Title input
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
            # Rich text editor for notes
            content = st.text_area(
                "Material Content", 
                value=st.session_state.material_form_state["text_content"],
                height=200, 
                placeholder="Enter your notes or material content here..."
            )
            
            # Add highlight button
            if st.button("Add Highlight"):
                highlight_text = st.text_input("Enter text to highlight")
                if highlight_text:
                    st.session_state.material_form_state["highlights"].append(highlight_text)
            
            # Display current highlights
            if st.session_state.material_form_state["highlights"]:
                st.write("Current Highlights:")
                for i, highlight in enumerate(st.session_state.material_form_state["highlights"]):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{highlight}**")
                    with col2:
                        if st.button("Remove", key=f"remove_highlight_{i}"):
                            st.session_state.material_form_state["highlights"].pop(i)
                            st.rerun()
            
            # Image upload
            uploaded_images = st.file_uploader(
                "Add Images to Notes",
                type=["png", "jpg", "jpeg"],
                accept_multiple_files=True
            )
            
            if uploaded_images:
                for image in uploaded_images:
                    image_bytes = image.read()
                    image_b64 = base64.b64encode(image_bytes).decode()
                    st.session_state.material_form_state["images"].append({
                        "name": image.name,
                        "data": image_b64
                    })
            
            st.session_state.material_form_state["text_content"] = content
            
        elif source_type == "Upload Notes":
            uploaded_file = st.file_uploader(
                "Upload Notes",
                type=["txt", "docx"],
                key="material_upload"
            )
        
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
                try:
                    file_bytes = uploaded_file.read()
                    file_name = uploaded_file.name
                    
                    if file_name.endswith('.txt'):
                        file_content = file_bytes.decode('utf-8')
                    elif file_name.endswith('.docx'):
                        doc = docx.Document(BytesIO(file_bytes))
                        file_content = "\n".join([paragraph.text for paragraph in doc.paragraphs])
                    else:
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
                    "created_at": datetime.now(),
                    "highlights": st.session_state.material_form_state["highlights"],
                    "images": st.session_state.material_form_state["images"],
                    "last_edited": datetime.now()
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
                    "difficulty": "intermediate",
                    "highlights": [],
                    "images": []
                }
                st.rerun()
            else:
                st.toast("Please fill in all required fields", icon="⚠️")
    
    # Display saved materials
    st.subheader("My Materials")
    
    # Query the database for user's materials
    materials_collection = db["user_materials"]
    saved_materials = list(materials_collection.find({"user_id": user_id}))
    
    if saved_materials:
        for material in saved_materials:
            with st.expander(f"{material['title']} ({material['category']})"):
                # Display material content
                if material["source_type"] == "Text Note":
                    st.write(material["content"])
                    
                    # Display highlights
                    if material.get("highlights"):
                        st.write("Highlights:")
                        for highlight in material["highlights"]:
                            st.markdown(f"**{highlight}**")
                    
                    # Display images
                    if material.get("images"):
                        st.write("Images:")
                        for image in material["images"]:
                            st.image(base64.b64decode(image["data"]), caption=image["name"])
                    
                    # Edit and Delete buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Edit Material", key=f"edit_{material['_id']}"):
                            st.session_state.material_form_state = {
                                "title": material["title"],
                                "source_type": material["source_type"],
                                "text_content": material["content"],
                                "category": material["category"],
                                "difficulty": material["difficulty"],
                                "highlights": material.get("highlights", []),
                                "images": material.get("images", [])
                            }
                            st.rerun()
                    with col2:
                        if st.button("Delete Material", key=f"delete_{material['_id']}"):
                            if st.button("Confirm Delete", key=f"confirm_delete_{material['_id']}"):
                                materials_collection.delete_one({"_id": material["_id"]})
                                st.success("Material deleted successfully!")
                                st.rerun()
                elif material["source_type"] == "URL":
                    st.write(f"URL: {material['source']}")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Open URL", key=f"url_{material['_id']}"):
                            webbrowser.open(material["source"])
                    with col2:
                        if st.button("Delete Material", key=f"delete_{material['_id']}"):
                            if st.button("Confirm Delete", key=f"confirm_delete_{material['_id']}"):
                                materials_collection.delete_one({"_id": material["_id"]})
                                st.success("Material deleted successfully!")
                                st.rerun()
                else:
                    st.write(f"File: {material['file_name']}")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Download File", key=f"download_{material['_id']}"):
                            # Handle file download
                            pass
                    with col2:
                        if st.button("Delete Material", key=f"delete_{material['_id']}"):
                            if st.button("Confirm Delete", key=f"confirm_delete_{material['_id']}"):
                                materials_collection.delete_one({"_id": material["_id"]})
                                st.success("Material deleted successfully!")
                                st.rerun()
    else:
        st.info("You haven't added any materials yet.")
