import streamlit as st
from streamlit_lottie import st_lottie
import requests
from database import add_qa_question, update_qa_answer
from ai_engine import answer_question
from pages.utils import create_qa_card
from granite_model import generate_granite_response
from datetime import datetime

def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Lottie animation for Q&A
lottie_qa = load_lottie_url("https://assets2.lottiefiles.com/packages/lf20_kyu7xb1v.json")

def show_qa(db, ai_models):
    """Display the Q&A page"""
    st.title("❓ Q&A")
    
    # Add animation to the top
    st_lottie(lottie_qa, height=180, key="qa-anim")
    
    # Get the current user ID and username
    user_id = st.session_state.get("user_id", "demo_student_id")
    username = st.session_state.get("username", "Demo Student")
    
    # Tabs for Questions, Ask Question, and My Questions
    tab1, tab2, tab3 = st.tabs(["Browse Questions", "Ask Question", "My Questions"])
    
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
        # Get unique topics from existing questions
        qa_collection = db["qa_questions"]
        existing_topics = qa_collection.distinct("topic")
        topics = ["All"] + sorted(list(set(existing_topics)))
        selected_topic = st.selectbox("Filter by Topic", topics)
    
    with col2:
        # Status filter
        status_options = ["All", "Answered", "Unanswered"]
        status = st.selectbox("Filter by Status", status_options)
    
    # Search box
    search_query = st.text_input("Search Questions", "")
    
    # Query the database for questions
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
    
    # Get existing topics and add "Other" option
    qa_collection = db["qa_questions"]
    existing_topics = qa_collection.distinct("topic")
    topics = sorted(list(set(existing_topics))) + ["Other"]
    
    # Topic selection
    topic_selection = st.selectbox("Topic", topics)
    
    # If 'Other' is selected, allow custom topic input
    if topic_selection == "Other":
        custom_topic = st.text_input("Please specify the topic:")
        topic = custom_topic if custom_topic else "Other"
    else:
        topic = topic_selection
    
    # Question input
    question_text = st.text_area("Your Question", height=100)
    
    # Submit button
    if st.button("Submit Question"):
        if question_text and topic:
            with st.spinner("Processing your question..."):
                try:
                    # Add the question to the database
                    question_id = add_qa_question(db, user_id, username, question_text, question_text, topic)
                    
                    # Generate AI answer using IBM Granite model
                    prompt = f"""
You are an expert tutor. Answer the following question in a clear, concise, and accurate manner.

Question: {question_text}
Topic: {topic}

Instructions:
- Provide a direct answer first.
- If the question is ambiguous, state your assumptions.
- Use examples, code, or references if helpful.
- Keep the explanation relevant to the question and avoid generic information.

Answer:
"""
                    answer_content = generate_granite_response(
                        ai_models["granite_model"],
                        prompt,
                        max_tokens=1000
                    )
                    
                    if answer_content and not answer_content.startswith("Error:"):
                        ai_answer = f"""## Answer to: {question_text}\n\n{answer_content}\n\n---\n*This answer was generated using IBM's Granite model, trained on a diverse dataset of educational content.*"""
                    else:
                        # Fallback to basic answer if Granite model fails
                        ai_answer = f"""## Answer to: {question_text}\n\nThank you for your question about {topic}. Here's a comprehensive answer:\n\n{answer_question(ai_models, question_text, question_text, topic)}"""
                    
                    update_qa_answer(db, question_id, ai_answer)
                    st.success("Question submitted and answered!")
                    st.subheader("Answer:")
                    st.markdown(ai_answer)
                    if st.button("View All Questions"):
                        st.rerun()
                except Exception as e:
                    st.error(f"Error processing your question: {str(e)}")
                    st.info("Please try again or contact support if the issue persists.")
        else:
            if not question_text:
                st.warning("Please enter your question.")
            if topic_selection == "Other" and not topic:
                st.warning("Please specify a topic.")
    
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
            with st.container():
                st.subheader(question.get("title", "Untitled Question"))
                st.write(question.get("content", ""))
                st.caption(f"Topic: {question.get('topic', 'Unspecified')}")
                
                if question.get("answered"):
                    st.markdown("### Answer:")
                    st.markdown(question.get("ai_answer", ""))
                else:
                    st.info("This question is waiting for an answer.")
                
                st.divider()
    else:
        st.info("You haven't asked any questions yet.")
