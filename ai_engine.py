import os
import streamlit as st
import pandas as pd
import numpy as np
from granite_model import initialize_granite_model, generate_granite_response

def load_ai_models():
    """Load AI models for use in the application"""
    try:
        # Setup IBM Granite model
        granite_model = initialize_granite_model()
        
        if granite_model and "model_name" in granite_model:
            st.sidebar.info(f"🤖 Using {granite_model['model_name']}")
        else:
            st.sidebar.info("⚠️ Using simulated AI responses for demo purposes")
        
        # Return a dictionary with AI model data
        return {
            "content_generation": True,
            "assessment_feedback": True,
            "qa_answer": True,
            "course_recommendation": True,
            "simulator": True,
            "granite_model": granite_model
        }
    except Exception as e:
        st.error(f"Failed to load AI models: {e}")
        return None

def generate_content(ai_models, topic, difficulty="intermediate", learning_style="visual"):
    """Generate educational content on a specific topic"""
    try:
        if ai_models and "content_generation" in ai_models:
            # Simulated AI content generation for demo purposes
            return f"""
            # {topic.title()} - {difficulty.capitalize()} Level

            ## Introduction
            Welcome to this {learning_style} guide on {topic}. This material is designed for {difficulty} level students.

            ## Key Concepts
            1. **First Key Concept**: This is an important aspect of {topic} that forms the foundation.
               - Example: Real-world application of this concept.
               - Visual representation: Imagine this concept as a building block.

            2. **Second Key Concept**: Another critical element to understand about {topic}.
               - Example: How this applies in practical scenarios.
               - Related theories and frameworks.

            3. **Third Key Concept**: Advanced understanding of {topic} requires mastery of this.
               - Connections to previous concepts.
               - Common misconceptions and how to avoid them.

            ## Practice Applications
            Here are some ways you can apply what you've learned:
            - Application 1: Description of how to apply the knowledge.
            - Application 2: Another practical use case.
            - Application 3: More advanced application for deeper understanding.

            ## Summary
            In this lesson on {topic}, we've covered several key concepts including their practical applications. 
            For {difficulty} learners with a preference for {learning_style} learning, these concepts should now be clearer.
            Continue practicing to reinforce your understanding!
            """
        else:
            return "AI content generation not available. Please try again later."
    except Exception as e:
        st.error(f"Error generating content: {e}")
        return "An error occurred while generating content. Please try again."

def evaluate_answer(ai_models, question, student_answer, reference_answer):
    """Evaluate a student's answer and provide feedback"""
    try:
        if ai_models and "assessment_feedback" in ai_models:
            # Simulated AI evaluation for demo purposes
            if len(student_answer) < 10:
                evaluation = "Your answer is too brief. Consider expanding on your ideas."
            elif any(keyword in student_answer.lower() for keyword in reference_answer.lower().split()[:5]):
                evaluation = "Good start! Your answer includes some key concepts, but could be more comprehensive."
            else:
                evaluation = "Your answer shows understanding of the topic. Well done!"
                
            return f"""
            ## Evaluation of Your Answer

            **Question:** {question}

            **Your answer:** {student_answer}

            **Feedback:**
            {evaluation}

            **Things to consider:**
            - Have you included all the key points from the lesson?
            - Is your explanation clear and well-structured?
            - Consider adding specific examples to strengthen your answer.

            Keep practicing and refining your understanding!
            """
        else:
            return "AI evaluation not available. Please try again later."
    except Exception as e:
        st.error(f"Error evaluating answer: {e}")
        return "An error occurred while evaluating your answer. Please try again."

def answer_question(ai_models, title, content, topic):
    """Generate an answer for a Q&A question"""
    try:
        if ai_models and "qa_answer" in ai_models:
            # Simulated AI Q&A response for demo purposes
            return f"""
            ## Answer to: {title}

            Thank you for your question about {topic}. 

            {content}

            Based on educational best practices and current understanding of {topic}, here's a comprehensive answer:

            The key to understanding this concept is to recognize that {topic} involves multiple interconnected elements. 
            First, consider the fundamental principles that govern this area. These include [principle 1], [principle 2], and [principle 3].

            When applying these concepts, it's helpful to think about real-world examples such as:
            1. Example scenario demonstrating the first principle
            2. Another practical application showing how this works
            3. A common challenge and how to overcome it using these principles

            Additional resources you might find helpful:
            - Recommended reading on {topic}
            - Practice exercises to reinforce these concepts
            - Related topics that would enhance your understanding

            I hope this helps with your question! Feel free to ask if you need further clarification.
            """
        else:
            return "AI Q&A not available. Please try again later."
    except Exception as e:
        st.error(f"Error answering question: {e}")
        return "An error occurred while generating an answer. Please try again."

def get_course_recommendations(ai_models, current_courses, interests, learning_style, recent_performance):
    """Generate personalized course recommendations"""
    try:
        if ai_models and "course_recommendation" in ai_models:
            # Simulated AI recommendation for demo purposes
            interests_list = ", ".join(interests) if isinstance(interests, list) else interests
            
            return f"""
            ## Personalized Learning Recommendations

            Based on your current progress and interests in {interests_list}, here are some recommendations to enhance your learning journey:

            1. **Next Course Recommendation**: Consider exploring "Advanced Applications of {interests_list if isinstance(interests, str) else interests[0] if interests else 'Your Subject'}"
               - This would build upon your current knowledge
               - Aligns with your {learning_style} learning style
               - Would help improve your performance in areas where you scored {recent_performance}

            2. **Skill Enhancement**: To complement your current courses, focus on developing skills in:
               - Practical application of theoretical concepts
               - Problem-solving techniques specific to your field
               - Collaborative learning opportunities with peers

            These recommendations are personalized based on your unique learning profile and will help you progress effectively in your educational journey.
            """
        else:
            return "AI recommendation not available. Please try again later."
    except Exception as e:
        st.error(f"Error generating recommendations: {e}")
        return "An error occurred while generating recommendations. Please try again."

def generate_practice_questions(ai_models, topic, difficulty="intermediate", num_questions=3):
    """Generate practice questions on a specific topic"""
    try:
        if ai_models:
            # Create structured practice questions based on the topic
            questions = []
            
            # Define difficulty adjustments
            complexity = {
                "beginner": "basic, fundamental concepts with straightforward answers",
                "intermediate": "moderately complex concepts that require some analysis",
                "advanced": "complex, in-depth concepts that require critical thinking"
            }
            
            # Generate different question types based on topic
            if topic.lower() in ["python", "programming", "coding"]:
                questions = [
                    {
                        "question": "What is the output of the following Python code?\n\nx = [1, 2, 3]\ny = x\ny.append(4)\nprint(x)",
                        "options": [
                            "A) [1, 2, 3]",
                            "B) [1, 2, 3, 4]",
                            "C) [4, 1, 2, 3]",
                            "D) Error"
                        ],
                        "correct_answer": 1,  # B is correct (index 1)
                        "explanation": "In Python, assignment operations create references to the same object, not copies. When we modify y by appending 4, we're also modifying x since they reference the same list object."
                    },
                    {
                        "question": "Which of the following is NOT a valid way to create a dictionary in Python?",
                        "options": [
                            "A) dict(a=1, b=2)",
                            "B) {'a': 1, 'b': 2}",
                            "C) dict([('a', 1), ('b', 2)])",
                            "D) {a=1, b=2}"
                        ],
                        "correct_answer": 3,  # D is correct (index 3)
                        "explanation": "Option D is invalid syntax for dictionary creation in Python. The correct syntax would be {'a': 1, 'b': 2} or dict(a=1, b=2) or dict([('a', 1), ('b', 2)])."
                    },
                    {
                        "question": "What is the primary purpose of the __init__ method in Python classes?",
                        "options": [
                            "A) To initialize class variables",
                            "B) To initialize instance variables when an object is created",
                            "C) To define class methods",
                            "D) To end the execution of a program"
                        ],
                        "correct_answer": 1,  # B is correct (index 1)
                        "explanation": "The __init__ method in Python is used to initialize instance variables when an object is created. It's called automatically when you create a new instance of a class."
                    }
                ]
            elif topic.lower() in ["data science", "machine learning", "ai"]:
                questions = [
                    {
                        "question": "Which of the following is NOT a supervised learning algorithm?",
                        "options": [
                            "A) Linear Regression",
                            "B) K-means Clustering",
                            "C) Support Vector Machines",
                            "D) Logistic Regression"
                        ],
                        "correct_answer": 1,  # B is correct (index 1)
                        "explanation": "K-means Clustering is an unsupervised learning algorithm used for finding clusters in data. Linear Regression, Support Vector Machines, and Logistic Regression are all supervised learning algorithms."
                    },
                    {
                        "question": "What is the purpose of regularization in machine learning?",
                        "options": [
                            "A) To increase model complexity",
                            "B) To decrease training time",
                            "C) To prevent overfitting",
                            "D) To improve model interpretability"
                        ],
                        "correct_answer": 2,  # C is correct (index 2)
                        "explanation": "Regularization is used to prevent overfitting by adding a penalty term to the loss function, which discourages the model from learning overly complex patterns that may not generalize well to new data."
                    },
                    {
                        "question": "Which of the following metrics is most appropriate for evaluating a classification model on an imbalanced dataset?",
                        "options": [
                            "A) Accuracy",
                            "B) F1 Score",
                            "C) Mean Squared Error",
                            "D) R-squared"
                        ],
                        "correct_answer": 1,  # B is correct (index 1)
                        "explanation": "The F1 Score is a good metric for imbalanced datasets as it combines precision and recall. Accuracy can be misleading on imbalanced datasets, while MSE and R-squared are typically used for regression problems."
                    }
                ]
            elif topic.lower() in ["mathematics", "math", "algebra", "calculus"]:
                questions = [
                    {
                        "question": "What is the derivative of f(x) = x³ + 2x² - 5x + 3?",
                        "options": [
                            "A) 3x² + 4x - 5",
                            "B) 3x² + 4x + 5",
                            "C) x² + 4x - 5",
                            "D) 3x² - 4x - 5"
                        ],
                        "correct_answer": 0,  # A is correct (index 0)
                        "explanation": "The derivative of x³ is 3x², the derivative of 2x² is 4x, the derivative of -5x is -5, and the derivative of the constant 3 is 0. Adding these together gives 3x² + 4x - 5."
                    },
                    {
                        "question": "Solve the equation: 2x² - 5x - 3 = 0",
                        "options": [
                            "A) x = 3 or x = -0.5",
                            "B) x = 3 or x = 0.5",
                            "C) x = -3 or x = 0.5",
                            "D) x = -3 or x = -0.5"
                        ],
                        "correct_answer": 0,  # A is correct (index 0)
                        "explanation": "Using the quadratic formula x = (-b ± √(b²-4ac))/(2a) with a=2, b=-5, c=-3, we get x = (5 ± √(25+24))/4 = (5 ± √49)/4 = (5 ± 7)/4, which gives x = 3 or x = -0.5."
                    },
                    {
                        "question": "What is the value of ∫(2x + 3) dx?",
                        "options": [
                            "A) x² + 3x",
                            "B) x² + 3x + C",
                            "C) 2x + 3 + C",
                            "D) 2(x² + 3x)"
                        ],
                        "correct_answer": 1,  # B is correct (index 1)
                        "explanation": "The integral of 2x is x², the integral of 3 is 3x, and we need to add a constant of integration C. So ∫(2x + 3) dx = x² + 3x + C."
                    }
                ]
            else:
                # Generic questions for other topics
                questions = [
                    {
                        "question": f"What is a key principle of {topic}?",
                        "options": [
                            f"A) {topic} is primarily focused on theoretical concepts without practical applications",
                            f"B) {topic} integrates multiple disciplines to solve complex problems",
                            f"C) {topic} was developed primarily in the 21st century",
                            f"D) {topic} is mainly used in academic research but rarely in industry"
                        ],
                        "correct_answer": 1,  # B is correct (index 1)
                        "explanation": f"{topic} is known for its interdisciplinary approach, integrating knowledge from various fields to address complex problems effectively."
                    },
                    {
                        "question": f"Which statement best describes the relationship between {topic} and critical thinking?",
                        "options": [
                            f"A) {topic} replaces the need for critical thinking with algorithmic procedures",
                            f"B) {topic} and critical thinking are unrelated disciplines",
                            f"C) {topic} enhances critical thinking by providing analytical frameworks",
                            f"D) Critical thinking is only relevant to theoretical aspects of {topic}"
                        ],
                        "correct_answer": 2,  # C is correct (index 2)
                        "explanation": f"{topic} provides structured frameworks that enhance critical thinking by encouraging systematic analysis, evaluation of evidence, and logical reasoning."
                    },
                    {
                        "question": f"Which of the following best represents an application of {topic}?",
                        "options": [
                            f"A) Developing theoretical models without practical implementation",
                            f"B) Applying established principles to solve novel problems",
                            f"C) Memorizing facts and procedures",
                            f"D) Working exclusively with qualitative data"
                        ],
                        "correct_answer": 1,  # B is correct (index 1)
                        "explanation": f"A key application of {topic} involves applying established principles and methodologies to address new and emerging problems, demonstrating its practical value."
                    }
                ]
            
            # Adjust number of questions if needed
            if len(questions) > num_questions:
                questions = questions[:num_questions]
            elif len(questions) < num_questions:
                # Add generic questions if we need more
                for i in range(len(questions), num_questions):
                    questions.append({
                        "question": f"Question {i+1}: According to modern research, what is a significant factor in understanding {topic}?",
                        "options": [
                            f"A) Historical development is irrelevant to understanding {topic}",
                            f"B) Comprehensive knowledge of {topic} requires understanding its foundational principles",
                            f"C) {topic} is best learned through memorization alone",
                            f"D) {topic} concepts are unchanging and not subject to revision"
                        ],
                        "correct_answer": 1,  # B is correct (index 1)
                        "explanation": f"Understanding the foundational principles of {topic} is essential for developing comprehensive knowledge, as these principles provide the framework for all advanced concepts."
                    })
                    
            # Format the questions for display
            formatted_questions = f"# Practice Questions on {topic} ({difficulty} level)\n\n"
            
            for i, q in enumerate(questions):
                formatted_questions += f"## Question {i+1}\n"
                formatted_questions += f"{q['question']}\n\n"
                formatted_questions += "**Options:**\n"
                for option in q['options']:
                    formatted_questions += f"{option}\n"
                formatted_questions += f"\n**Correct Answer:** {q['options'][q['correct_answer']][0]}\n\n"
                formatted_questions += f"**Explanation:** {q['explanation']}\n\n"
                
            return formatted_questions
        else:
            return "AI model not available. Please try again later."
    except Exception as e:
        st.error(f"Error generating practice questions: {e}")
        return "An error occurred while generating practice questions. Please try again."

def summarize_learning_material(ai_models, content, max_length=500):
    """Summarize learning material to a concise version"""
    try:
        if ai_models:
            # Simulated summary for demo purposes
            # Just return first part of the content up to max_length
            if len(content) > max_length:
                summary = content[:max_length] + "..."
            else:
                summary = content
                
            return f"""
            ## Summary of Learning Material
            
            {summary}
            
            **Key takeaways:**
            - First important concept from the material
            - Second important concept
            - Third important concept
            
            This summary captures the essential points while omitting supplementary details.
            """
        else:
            return "AI model not available. Please try again later."
    except Exception as e:
        st.error(f"Error summarizing content: {e}")
        return "An error occurred while summarizing the content. Please try again."
