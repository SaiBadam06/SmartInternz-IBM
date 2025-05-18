import streamlit as st
import pandas as pd
from database import save_user_assessment_result
from ai_engine import evaluate_answer, generate_practice_questions
from pages.utils import create_assessment_card
from datetime import datetime

def show_assessments(db, ai_models):
    """Display the assessments page"""
    st.title("📝 Assessments")
    
    # Get the current user ID
    user_id = st.session_state.get("user_id", "demo_student_id")
    
    # If an assessment is in progress, show it
    if "current_assessment" in st.session_state:
        display_assessment(db, ai_models, user_id)
        return
    
    # Tabs for Available Assessments, Results, and Practice
    tab1, tab2, tab3 = st.tabs(["Available Assessments", "Results", "Practice Questions"])
    
    with tab1:
        show_available_assessments(db, user_id)
    
    with tab2:
        show_assessment_results(db, user_id)
    
    with tab3:
        show_practice_questions(db, ai_models, user_id)

def show_available_assessments(db, user_id):
    """Show available assessments for the user"""
    st.header("Available Assessments")
    
    # Get user's enrolled courses
    progress_collection = db["progress"]
    user_progress = list(progress_collection.find({"user_id": user_id}))
    enrolled_course_ids = [p["course_id"] for p in user_progress]
    
    # Get assessments for enrolled courses
    assessments_collection = db["assessments"]
    assessments = list(assessments_collection.find({"course_id": {"$in": enrolled_course_ids}}))
    
    if assessments:
        # Get course names for display
        courses_collection = db["courses"]
        courses = {c["_id"]: c["title"] for c in courses_collection.find({"_id": {"$in": enrolled_course_ids}})}
        
        # Group assessments by course
        for course_id in enrolled_course_ids:
            course_assessments = [a for a in assessments if a["course_id"] == course_id]
            if course_assessments:
                st.subheader(courses.get(course_id, "Unknown Course"))
                
                for assessment in course_assessments:
                    create_assessment_card(assessment, start_assessment)
    else:
        st.info("No assessments available for your courses.")

def show_assessment_results(db, user_id):
    """Show results of completed assessments"""
    st.header("Assessment Results")
    
    # Get user's assessment results
    assessment_results = db["assessment_results"]
    results = list(assessment_results.find({"user_id": user_id}))
    
    if results:
        # Get assessment details
        assessments_collection = db["assessments"]
        assessment_ids = [r["assessment_id"] for r in results]
        assessments = {a["_id"]: a for a in assessments_collection.find({"_id": {"$in": assessment_ids}})}
        
        # Get course details
        course_ids = [a["course_id"] for a in assessments.values() if "course_id" in a]
        courses_collection = db["courses"]
        courses = {c["_id"]: c["title"] for c in courses_collection.find({"_id": {"$in": course_ids}})}
        
        # Display results in a table
        result_data = []
        for r in results:
            assessment = assessments.get(r["assessment_id"], {})
            course_id = assessment.get("course_id", "")
            result_data.append({
                "Assessment": assessment.get("title", "Unknown Assessment"),
                "Course": courses.get(course_id, "Unknown Course"),
                "Score": f"{r.get('score', 0)}%",
                "Completed": r.get("completed_at", "Unknown")
            })
        
        result_df = pd.DataFrame(result_data)
        st.dataframe(result_df)
        
        # Display a bar chart of scores
        st.subheader("Performance Summary")
        
        chart_data = pd.DataFrame({
            "Assessment": [r["Assessment"] for r in result_data],
            "Score": [float(r["Score"].strip("%")) for r in result_data]
        })
        
        st.bar_chart(chart_data.set_index("Assessment"))
        
        # Option to view detailed results
        selected_assessment = st.selectbox("View Detailed Results", ["Select an assessment..."] + [r["Assessment"] for r in result_data])
        
        if selected_assessment != "Select an assessment...":
            # Find the corresponding result
            selected_result = next((r for r in results if assessments.get(r["assessment_id"], {}).get("title", "") == selected_assessment), None)
            
            if selected_result:
                st.subheader(f"Detailed Results for {selected_assessment}")
                
                # Find the assessment to get questions
                assessment = assessments.get(selected_result["assessment_id"], {})
                questions = assessment.get("questions", [])
                
                # Display each question and answer
                for i, question in enumerate(questions):
                    st.markdown(f"**Question {i+1}:** {question.get('text', '')}")
                    
                    answer = selected_result.get("answers", {}).get(question.get("question_id", ""), "No answer provided")
                    
                    if question.get("type") == "multiple_choice":
                        correct = answer == question.get("correct_answer", "")
                        st.markdown(f"Your answer: {answer} {'✅' if correct else '❌'}")
                        if not correct:
                            st.markdown(f"Correct answer: {question.get('correct_answer', '')}")
                    else:
                        st.markdown(f"Your answer: {answer}")
                        st.markdown(f"Sample answer: {question.get('sample_answer', 'No sample answer provided')}")
    else:
        st.info("You haven't completed any assessments yet.")

def show_practice_questions(db, ai_models, user_id):
    """Show interface for generating practice questions"""
    st.header("Practice Questions")
    
    st.markdown("""
    Generate practice questions on any topic to test your knowledge.
    These questions are AI-generated and adapt to your specified difficulty level.
    """)
    
    # Topic input
    topic = st.text_input("Topic", "")
    
    # Difficulty selection
    difficulty_options = ["beginner", "intermediate", "advanced"]
    difficulty = st.select_slider("Difficulty", options=difficulty_options, value="intermediate")
    
    # Number of questions
    num_questions = st.slider("Number of Questions", min_value=1, max_value=10, value=3)
    
    # Generate button
    if st.button("Generate Practice Questions"):
        if topic:
            with st.spinner("Generating practice questions..."):
                questions = generate_practice_questions(ai_models, topic, difficulty, num_questions)
                
                # Display the generated questions
                st.subheader(f"Practice Questions: {topic}")
                st.write(questions)
                
                # Option to save these questions
                if st.button("Save to My Practice Questions"):
                    # Save the questions to the database
                    practice_collection = db["practice_questions"]
                    practice = {
                        "user_id": user_id,
                        "topic": topic,
                        "difficulty": difficulty,
                        "questions": questions,
                        "created_at": datetime.now()
                    }
                    practice_collection.insert_one(practice)
                    st.success("Practice questions saved to your collection!")
        else:
            st.warning("Please enter a topic.")
    
    # Display saved practice questions
    st.subheader("My Saved Practice Questions")
    
    # Query the database for saved practice questions
    practice_collection = db["practice_questions"]
    saved_practice = list(practice_collection.find({"user_id": user_id}))
    
    if saved_practice:
        for practice in saved_practice:
            with st.expander(f"{practice['topic']} ({practice['difficulty']})"):
                st.write(practice["questions"])
                
                # Option to delete these questions
                if st.button("Delete", key=f"delete_practice_{practice.get('_id', 'unknown')}"):
                    practice_collection.delete_one({"_id": practice["_id"]})
                    st.success("Practice questions deleted!")
                    st.rerun()
    else:
        st.info("You don't have any saved practice questions yet.")

def start_assessment(assessment_id):
    """Start an assessment"""
    st.session_state.current_assessment = assessment_id
    st.session_state.current_question = 0
    st.session_state.answers = {}
    st.rerun()

def display_assessment(db, ai_models, user_id):
    """Display the assessment in progress"""
    # Get the assessment from the database
    assessments_collection = db["assessments"]
    assessment = assessments_collection.find_one({"_id": st.session_state.current_assessment})
    
    if not assessment:
        st.error("Assessment not found.")
        st.session_state.pop("current_assessment", None)
        st.rerun()
        return
    
    # Display assessment title
    st.header(assessment["title"])
    st.markdown(assessment["description"])
    
    # Get the current question
    questions = assessment.get("questions", [])
    if not questions:
        st.error("No questions found in this assessment.")
        st.session_state.pop("current_assessment", None)
        st.rerun()
        return
    
    # Display progress
    total_questions = len(questions)
    current_q_index = st.session_state.current_question
    st.progress(current_q_index / total_questions)
    st.markdown(f"Question {current_q_index + 1} of {total_questions}")
    
    # Get the current question
    if current_q_index < total_questions:
        question = questions[current_q_index]
        
        # Display the question
        st.subheader(question["text"])
        
        # Handle different question types
        question_id = question.get("question_id", f"q{current_q_index + 1}")
        
        if question["type"] == "multiple_choice":
            options = question.get("options", [])
            answer = st.radio("Select your answer:", options, key=f"answer_{question_id}")
            
            if st.button("Next"):
                # Save the answer
                st.session_state.answers[question_id] = answer
                
                # Move to the next question
                st.session_state.current_question += 1
                st.rerun()
        
        elif question["type"] == "open_ended":
            answer = st.text_area("Your answer:", key=f"answer_{question_id}", height=150)
            
            if st.button("Next"):
                # Save the answer
                st.session_state.answers[question_id] = answer
                
                # Move to the next question
                st.session_state.current_question += 1
                st.rerun()
    
    else:
        # Assessment completed
        st.success("Assessment completed!")
        
        # Calculate the score for multiple choice questions
        score = 0
        total_mc_questions = 0
        
        for q in questions:
            if q["type"] == "multiple_choice":
                question_id = q.get("question_id", f"q{questions.index(q) + 1}")
                if st.session_state.answers.get(question_id) == q.get("correct_answer"):
                    score += 1
                total_mc_questions += 1
        
        # Calculate percentage score
        if total_mc_questions > 0:
            percentage_score = (score / total_mc_questions) * 100
        else:
            percentage_score = 0
        
        st.markdown(f"Your score for multiple choice questions: **{percentage_score:.1f}%**")
        
        # For open-ended questions, provide feedback using AI
        open_ended_feedback = []
        
        for q in questions:
            if q["type"] == "open_ended":
                question_id = q.get("question_id", f"q{questions.index(q) + 1}")
                student_answer = st.session_state.answers.get(question_id, "")
                
                if student_answer:
                    reference_answer = q.get("sample_answer", "")
                    feedback = evaluate_answer(ai_models, q["text"], student_answer, reference_answer)
                    
                    open_ended_feedback.append({
                        "question": q["text"],
                        "answer": student_answer,
                        "feedback": feedback
                    })
        
        # Display feedback for open-ended questions
        if open_ended_feedback:
            st.subheader("Feedback on Open-Ended Questions")
            
            for item in open_ended_feedback:
                with st.expander(item["question"]):
                    st.write("Your answer:")
                    st.write(item["answer"])
                    st.write("Feedback:")
                    st.write(item["feedback"])
        
        # Save the assessment result to the database
        save_user_assessment_result(db, user_id, assessment["_id"], percentage_score, st.session_state.answers)
        
        # Button to return to assessments
        if st.button("Return to Assessments"):
            st.session_state.pop("current_assessment", None)
            st.session_state.pop("current_question", None)
            st.session_state.pop("answers", None)
            st.rerun()
