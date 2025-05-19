import streamlit as st
from database import add_qa_question, update_qa_answer
from ai_engine import answer_question
from pages.utils import create_qa_card

def show_qa(db, ai_models):
    """Display the Q&A page"""
    st.title("❓ Q&A")
    
    # Get the current user ID and username
    user_id = st.session_state.get("user_id", "demo_student_id")
    username = st.session_state.get("username", "Demo Student")
    
    # Tabs for Questions, Ask Question, and My Questions
    tab1, tab2, tab3 = st.tabs(["Browse Questions", "Ask a Question", "My Questions"])
    
    with tab1:
        show_questions(db)
    
    with tab2:
        ask_question(db, ai_models, user_id, username)
    
    with tab3:
        show_my_questions(db, user_id)

def show_questions(db):
    """Show Q&A questions with filtering options"""
    st.header("Browse Questions")
    
    # Filtering options
    col1, col2 = st.columns(2)
    
    with col1:
        # Topic filter
        topics = ["All", "Python", "Data Science", "Mathematics", "Statistics", "Machine Learning", "Computer Science", "Other"]
        selected_topic = st.selectbox("Filter by Topic", topics)
    
    with col2:
        # Status filter
        status_options = ["All", "Answered", "Unanswered"]
        status = st.selectbox("Filter by Status", status_options)
    
    # Search box
    search_query = st.text_input("Search Questions", "")
    
    # Query the database for questions
    qa_collection = db["qa_questions"]
    query = {}
    
    if selected_topic != "All":
        query["topic"] = selected_topic
    
    if status == "Answered":
        query["answered"] = True
    elif status == "Unanswered":
        query["answered"] = False
    
    if search_query:
        query["$or"] = [
            {"title": {"$regex": search_query, "$options": "i"}},
            {"content": {"$regex": search_query, "$options": "i"}}
        ]
    
    # Sort by newest first
    questions = list(qa_collection.find(query).sort("created_at", -1))
    
    if questions:
        # Display questions with unique indices
        for i, question in enumerate(questions):
            create_qa_card(question, index=f"browse_{i}")
    else:
        st.info("No questions found matching your criteria.")

def ask_question(db, ai_models, user_id, username):
    """Interface for asking a new question"""
    st.header("Ask a Question")
    
    st.markdown("""
    Ask any academic or learning-related question, and our AI-powered system will provide a detailed answer.
    Your question will also be visible to the community, where others can learn from it.
    """)
    
    # Topic selection
    topics = ["Python", "Data Science", "Mathematics", "Statistics", "Machine Learning", "Computer Science", "Other"]
    topic_selection = st.selectbox("Topic", topics)
    
    # If 'Other' is selected, allow custom topic input
    if topic_selection == "Other":
        custom_topic = st.text_input("Please specify the topic:")
        topic = custom_topic if custom_topic else "Other"
    else:
        topic = topic_selection
    
    # Question form
    title = st.text_input("Question Title")
    content = st.text_area("Question Details", height=150)
    
    # Submit button
    if st.button("Submit Question"):
        if title and content and topic:
            with st.spinner("Processing your question..."):
                # Add the question to the database
                question_id = add_qa_question(db, user_id, username, title, content, topic)
                
                # Generate AI answer using IBM Granite model if available
                if "granite_model" in ai_models and ai_models["granite_model"]:
                    from granite_model import generate_granite_response
                    try:
                        prompt = f"Question: {title}\n\nDetails: {content}\n\nTopic: {topic}\n\nPlease provide a detailed, accurate, and educational answer to this question."
                        answer_content = generate_granite_response(ai_models["granite_model"], prompt, max_tokens=1000)
                        ai_answer = f"## Answer to: {title}\n\n{answer_content}"
                    except Exception as e:
                        # Fall back to standard answer_question if there's an error
                        st.error(f"Error with advanced AI model: {str(e)}")
                        ai_answer = answer_question(ai_models, title, content, topic)
                else:
                    # Standard answer generation
                    ai_answer = answer_question(ai_models, title, content, topic)
                
                # Update the question with the AI answer
                update_qa_answer(db, question_id, ai_answer)
                
                st.success("Question submitted and answered!")
                
                # Display the answer
                st.subheader("Answer:")
                st.write(ai_answer)
                
                # Button to view all questions
                if st.button("View All Questions"):
                    st.rerun()
        else:
            if not title:
                st.warning("Please enter a question title.")
            if not content:
                st.warning("Please provide question details.")
            if topic_selection == "Other" and not topic:
                st.warning("Please specify a topic.")
    
    # Display tips for asking good questions
    with st.expander("Tips for Asking Good Questions"):
        st.markdown("""
        ### Tips for Asking Effective Questions
        
        1. **Be Specific** - Clearly state what you're trying to understand or solve.
        
        2. **Provide Context** - Include relevant background information and what you already know.
        
        3. **Show Your Work** - If you've attempted to solve a problem, share your approach.
        
        4. **Use Clear Formatting** - Format mathematical equations or code snippets properly.
        
        5. **Check for Duplicates** - Search first to see if your question has already been answered.
        
        6. **Use Proper Grammar** - Write clearly and check your spelling.
        
        7. **Ask One Question at a Time** - If you have multiple questions, submit them separately.
        
        Good questions receive better answers and help others who have similar questions!
        """)

def show_my_questions(db, user_id):
    """Show questions asked by the current user"""
    st.header("My Questions")
    
    # Query the database for user's questions
    qa_collection = db["qa_questions"]
    user_questions = list(qa_collection.find({"user_id": user_id}).sort("created_at", -1))
    
    if user_questions:
        # Display user's questions with unique indices
        for i, question in enumerate(user_questions):
            create_qa_card(question, index=f"my_{i}")
    else:
        st.info("You haven't asked any questions yet.")
