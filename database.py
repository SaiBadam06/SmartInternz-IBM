import os
import pymongo
import streamlit as st
from datetime import datetime
import pandas as pd

def initialize_db():
    """Initialize MongoDB connection and return client and database objects"""
    try:
        mongo_uri = os.getenv("MONGO_URI", "mongodb+srv://badamdeekshith:xeWmNvCbbzOi7yL7@cluster0.aecpd6m.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
        client = pymongo.MongoClient(mongo_uri)
        db = client["edututor_ai"]
        
        # Initialize collections if they don't exist
        create_initial_data(db)
        
        return client, db
    except Exception as e:
        st.error(f"Failed to connect to MongoDB: {e}")
        return None, None

def create_initial_data(db):
    """Create initial data in the database if collections are empty"""
    
    # Create users collection if it doesn't exist
    if "users" not in db.list_collection_names():
        users_collection = db["users"]
        # Create a demo student user
        demo_user = {
            "_id": "demo_student_id",
            "username": "Demo Student",
            "email": "demo@example.com",
            "role": "student",
            "created_at": datetime.now(),
            "preferences": {
                "learning_style": "visual",
                "difficulty_level": "intermediate",
                "interests": ["programming", "data science", "mathematics"]
            }
        }
        users_collection.insert_one(demo_user)
    
    # Create courses collection if it doesn't exist
    if "courses" not in db.list_collection_names():
        courses_collection = db["courses"]
        # Add some demo courses
        demo_courses = [
            {
                "_id": "course_python_basics",
                "title": "Python Programming Basics",
                "description": "An introduction to Python programming language fundamentals.",
                "category": "Computer Science",
                "difficulty": "beginner",
                "topics": ["variables", "data types", "control flow", "functions"],
                "created_at": datetime.now()
            },
            {
                "_id": "course_data_science_intro",
                "title": "Introduction to Data Science",
                "description": "Learn the fundamentals of data science with Python.",
                "category": "Data Science",
                "difficulty": "intermediate",
                "topics": ["data analysis", "visualization", "statistics", "machine learning basics"],
                "created_at": datetime.now()
            },
            {
                "_id": "course_math_algebra",
                "title": "Algebra Fundamentals",
                "description": "Master algebraic concepts for academic success.",
                "category": "Mathematics",
                "difficulty": "intermediate",
                "topics": ["equations", "functions", "graphing", "polynomials"],
                "created_at": datetime.now()
            }
        ]
        courses_collection.insert_many(demo_courses)
    
    # Create assessments collection if it doesn't exist
    if "assessments" not in db.list_collection_names():
        assessments_collection = db["assessments"]
        # Add some demo assessments
        demo_assessments = [
            {
                "_id": "assessment_python_basics",
                "title": "Python Basics Quiz",
                "course_id": "course_python_basics",
                "description": "Test your knowledge of Python fundamentals",
                "questions": [
                    {
                        "question_id": "q1",
                        "text": "What is the correct way to create a variable in Python?",
                        "type": "multiple_choice",
                        "options": ["var x = 5", "x = 5", "x := 5", "set x = 5"],
                        "correct_answer": "x = 5"
                    },
                    {
                        "question_id": "q2",
                        "text": "What is the output of: print(2 + 2 * 2)",
                        "type": "multiple_choice",
                        "options": ["6", "8", "4", "Error"],
                        "correct_answer": "6"
                    },
                    {
                        "question_id": "q3",
                        "text": "Explain how functions help with code reusability in Python.",
                        "type": "open_ended",
                        "sample_answer": "Functions allow code to be defined once and executed multiple times, promoting reusability and reducing redundancy. They can accept parameters and return values, making them versatile for different contexts."
                    }
                ],
                "created_at": datetime.now()
            },
            {
                "_id": "assessment_data_science",
                "title": "Data Science Concepts",
                "course_id": "course_data_science_intro",
                "description": "Evaluate your understanding of data science principles",
                "questions": [
                    {
                        "question_id": "q1",
                        "text": "Which Python library is most commonly used for data manipulation?",
                        "type": "multiple_choice",
                        "options": ["NumPy", "Pandas", "Matplotlib", "Scikit-learn"],
                        "correct_answer": "Pandas"
                    },
                    {
                        "question_id": "q2",
                        "text": "What does EDA stand for in data science?",
                        "type": "multiple_choice",
                        "options": ["External Data Analysis", "Exploratory Data Analysis", "Extended Data Architecture", "Efficient Data Algorithms"],
                        "correct_answer": "Exploratory Data Analysis"
                    }
                ],
                "created_at": datetime.now()
            }
        ]
        assessments_collection.insert_many(demo_assessments)
    
    # Create progress collection if it doesn't exist
    if "progress" not in db.list_collection_names():
        progress_collection = db["progress"]
        # Add some demo progress
        demo_progress = [
            {
                "user_id": "demo_student_id",
                "course_id": "course_python_basics",
                "completed_topics": ["variables", "data types"],
                "progress_percentage": 50,
                "quiz_scores": [
                    {"quiz_id": "quiz_variables", "score": 85},
                    {"quiz_id": "quiz_data_types", "score": 90}
                ],
                "last_updated": datetime.now()
            },
            {
                "user_id": "demo_student_id",
                "course_id": "course_data_science_intro",
                "completed_topics": ["data analysis"],
                "progress_percentage": 25,
                "quiz_scores": [
                    {"quiz_id": "quiz_data_analysis", "score": 75}
                ],
                "last_updated": datetime.now()
            }
        ]
        progress_collection.insert_many(demo_progress)
        
    # Create community posts collection if it doesn't exist
    if "community_posts" not in db.list_collection_names():
        posts_collection = db["community_posts"]
        # Add some demo posts
        demo_posts = [
            {
                "user_id": "system",
                "username": "System",
                "title": "Welcome to the EduTutor AI Community!",
                "content": "This is a space for students to connect, collaborate, and learn together. Feel free to share your questions, insights, and resources with others!",
                "topic": "General",
                "likes": 5,
                "comments": [],
                "created_at": datetime.now()
            },
            {
                "user_id": "demo_student_id",
                "username": "Demo Student",
                "title": "Looking for study partners in Data Science",
                "content": "I'm currently taking the Introduction to Data Science course and would love to connect with others who are learning similar topics. Anyone interested in forming a study group?",
                "topic": "Data Science",
                "likes": 2,
                "comments": [
                    {
                        "user_id": "system",
                        "username": "System",
                        "content": "Great idea! You can also check out the resources section for additional study materials.",
                        "created_at": datetime.now()
                    }
                ],
                "created_at": datetime.now()
            }
        ]
        posts_collection.insert_many(demo_posts)
        
    # Create Q&A collection if it doesn't exist
    if "qa_questions" not in db.list_collection_names():
        qa_collection = db["qa_questions"]
        # Add some demo questions
        demo_questions = [
            {
                "user_id": "demo_student_id",
                "username": "Demo Student",
                "title": "How do list comprehensions work in Python?",
                "content": "I'm confused about the syntax of list comprehensions. Can someone explain with examples?",
                "topic": "Python",
                "answered": True,
                "ai_answer": "List comprehensions provide a concise way to create lists based on existing lists. The basic syntax is: [expression for item in iterable if condition]. For example, to create a list of squares: squares = [x**2 for x in range(10)]. This is equivalent to using a for loop but more concise and often faster.",
                "likes": 3,
                "created_at": datetime.now()
            },
            {
                "user_id": "demo_student_id",
                "username": "Demo Student",
                "title": "What's the difference between mean, median, and mode?",
                "content": "I'm studying statistics and getting confused about when to use each of these measures of central tendency.",
                "topic": "Statistics",
                "answered": True,
                "ai_answer": "Mean is the average of all values (sum divided by count). Median is the middle value when data is sorted. Mode is the most frequently occurring value. Mean is sensitive to outliers, while median is more robust. Use mean for normally distributed data, median for skewed data, and mode for categorical data or when you need the most common value.",
                "likes": 2,
                "created_at": datetime.now()
            }
        ]
        qa_collection.insert_many(demo_questions)

def get_user_progress(db, user_id):
    """Get progress data for a user across all courses"""
    progress_collection = db["progress"]
    progress_data = list(progress_collection.find({"user_id": user_id}))
    return progress_data

def get_user_courses(db, user_id):
    """Get courses that the user is enrolled in"""
    progress_collection = db["progress"]
    user_progress = list(progress_collection.find({"user_id": user_id}))
    
    course_ids = [p["course_id"] for p in user_progress]
    
    courses_collection = db["courses"]
    courses = list(courses_collection.find({"_id": {"$in": course_ids}}))
    
    return courses

def get_course_recommendations(db, user_id):
    """Get course recommendations for a user based on their interests and progress"""
    users_collection = db["users"]
    courses_collection = db["courses"]
    
    # Get user preferences
    user = users_collection.find_one({"_id": user_id})
    interests = user.get("preferences", {}).get("interests", [])
    
    # Get user's current courses
    current_courses = get_user_courses(db, user_id)
    current_course_ids = [c["_id"] for c in current_courses]
    
    # Find courses matching user interests that the user is not already enrolled in
    recommended_courses = []
    if interests:
        for interest in interests:
            similar_courses = list(courses_collection.find({
                "_id": {"$nin": current_course_ids},
                "$or": [
                    {"category": {"$regex": interest, "$options": "i"}},
                    {"title": {"$regex": interest, "$options": "i"}},
                    {"description": {"$regex": interest, "$options": "i"}}
                ]
            }).limit(3))
            recommended_courses.extend(similar_courses)
    
    # If we don't have enough recommendations, add some popular courses
    if len(recommended_courses) < 3:
        additional_courses = list(courses_collection.find({
            "_id": {"$nin": current_course_ids + [c["_id"] for c in recommended_courses]}
        }).limit(3 - len(recommended_courses)))
        recommended_courses.extend(additional_courses)
    
    return recommended_courses[:3]  # Return at most 3 recommendations

def save_user_assessment_result(db, user_id, assessment_id, score, answers):
    """Save user's assessment results"""
    assessment_results = db["assessment_results"]
    
    # Check if this user has already taken this assessment
    existing_result = assessment_results.find_one({
        "user_id": user_id,
        "assessment_id": assessment_id
    })
    
    if existing_result:
        # Update existing result
        assessment_results.update_one(
            {"_id": existing_result["_id"]},
            {
                "$set": {
                    "score": score,
                    "answers": answers,
                    "completed_at": datetime.now()
                }
            }
        )
    else:
        # Create new result
        assessment_results.insert_one({
            "user_id": user_id,
            "assessment_id": assessment_id,
            "score": score,
            "answers": answers,
            "completed_at": datetime.now()
        })
    
    # Update user progress for the corresponding course
    assessments_collection = db["assessments"]
    assessment = assessments_collection.find_one({"_id": assessment_id})
    
    if assessment and "course_id" in assessment:
        progress_collection = db["progress"]
        progress = progress_collection.find_one({
            "user_id": user_id,
            "course_id": assessment["course_id"]
        })
        
        if progress:
            # Update quiz score in progress
            quiz_scores = progress.get("quiz_scores", [])
            
            # Check if this assessment is already in the quiz scores
            for i, quiz in enumerate(quiz_scores):
                if quiz["quiz_id"] == assessment_id:
                    quiz_scores[i] = {"quiz_id": assessment_id, "score": score}
                    break
            else:
                # This assessment wasn't in the quiz scores, so add it
                quiz_scores.append({"quiz_id": assessment_id, "score": score})
            
            # Calculate new progress percentage
            course = db["courses"].find_one({"_id": assessment["course_id"]})
            if course:
                topics = course.get("topics", [])
                completed_topics = progress.get("completed_topics", [])
                if topics:
                    new_progress = min(100, int((len(completed_topics) / len(topics)) * 100))
                else:
                    new_progress = progress.get("progress_percentage", 0)
                
                # Update progress
                progress_collection.update_one(
                    {"_id": progress["_id"]},
                    {
                        "$set": {
                            "quiz_scores": quiz_scores,
                            "progress_percentage": new_progress,
                            "last_updated": datetime.now()
                        }
                    }
                )

def get_learning_stats(db, user_id):
    """Get learning statistics for the dashboard"""
    progress_collection = db["progress"]
    progress_data = list(progress_collection.find({"user_id": user_id}))
    
    total_courses = len(progress_data)
    avg_progress = sum(p.get("progress_percentage", 0) for p in progress_data) / max(1, total_courses)
    
    quiz_scores = []
    for p in progress_data:
        quiz_scores.extend(p.get("quiz_scores", []))
    
    avg_score = sum(q.get("score", 0) for q in quiz_scores) / max(1, len(quiz_scores))
    
    # Get course names for progress data
    course_ids = [p["course_id"] for p in progress_data]
    courses_collection = db["courses"]
    courses = {c["_id"]: c["title"] for c in courses_collection.find({"_id": {"$in": course_ids}})}
    
    # Create formatted progress data with course names
    formatted_progress = []
    for p in progress_data:
        course_id = p["course_id"]
        formatted_progress.append({
            "course": courses.get(course_id, "Unknown Course"),
            "progress": p.get("progress_percentage", 0)
        })
    
    # Convert to DataFrame for easier visualization
    progress_df = pd.DataFrame(formatted_progress)
    
    # Create recent quiz scores data
    recent_quizzes = []
    for p in progress_data:
        for q in p.get("quiz_scores", []):
            recent_quizzes.append({
                "course": courses.get(p["course_id"], "Unknown Course"),
                "score": q.get("score", 0)
            })
    
    # Sort by score and get the 5 most recent
    recent_quizzes = sorted(recent_quizzes, key=lambda x: x["score"], reverse=True)[:5]
    quizzes_df = pd.DataFrame(recent_quizzes)
    
    return {
        "total_courses": total_courses,
        "avg_progress": avg_progress,
        "avg_score": avg_score,
        "progress_data": progress_df,
        "quiz_data": quizzes_df
    }

def add_community_post(db, user_id, username, title, content, topic):
    """Add a new community post"""
    posts_collection = db["community_posts"]
    post = {
        "user_id": user_id,
        "username": username,
        "title": title,
        "content": content,
        "topic": topic,
        "likes": 0,
        "comments": [],
        "created_at": datetime.now()
    }
    posts_collection.insert_one(post)

def add_qa_question(db, user_id, username, title, content, topic):
    """Add a new Q&A question"""
    qa_collection = db["qa_questions"]
    question = {
        "user_id": user_id,
        "username": username,
        "title": title,
        "content": content,
        "topic": topic,
        "answered": False,
        "ai_answer": "",
        "likes": 0,
        "created_at": datetime.now()
    }
    result = qa_collection.insert_one(question)
    return result.inserted_id

def update_qa_answer(db, question_id, ai_answer):
    """Update a Q&A question with AI-generated answer"""
    qa_collection = db["qa_questions"]
    qa_collection.update_one(
        {"_id": question_id},
        {
            "$set": {
                "answered": True,
                "ai_answer": ai_answer
            }
        }
    )
