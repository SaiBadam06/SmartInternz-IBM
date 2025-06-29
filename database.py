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
        # For demo purposes, create a fallback database
        try:
            # Create a fallback in-memory data structure
            st.warning("Using local memory storage for demo purposes")
            return setup_fallback_db()
        except Exception as e2:
            st.error(f"Fallback database also failed: {e2}")
            return None, None

def setup_fallback_db():
    """Setup a fallback database using a dictionary-based approach for demo purposes"""
    from datetime import datetime
    
    # Create a simple class to mimic MongoDB collection behavior
    class MockCollection:
        def __init__(self, name, initial_data=None):
            self.name = name
            self.data = initial_data or []
            self._id_counter = 1000  # Starting ID for new documents
            
        def find(self, query=None, *args, **kwargs):
            if query is None:
                query = {}
            
            # Simple implementation of find with basic filtering
            results = []
            for doc in self.data:
                match = True
                for k, v in query.items():
                    if k == "$or":
                        or_match = False
                        for or_clause in v:
                            or_clause_match = True
                            for or_k, or_v in or_clause.items():
                                if or_k in doc:
                                    if isinstance(or_v, dict) and "$regex" in or_v:
                                        # Very basic regex support
                                        pattern = or_v["$regex"].lower()
                                        if pattern not in str(doc[or_k]).lower():
                                            or_clause_match = False
                                    elif doc[or_k] != or_v:
                                        or_clause_match = False
                                else:
                                    or_clause_match = False
                            if or_clause_match:
                                or_match = True
                                break
                        if not or_match:
                            match = False
                    elif k == "$nin" and k in doc:
                        if doc[k] in v:
                            match = False
                    elif k in doc:
                        if isinstance(v, dict):
                            # Handle operators like $in, $nin
                            for op, op_val in v.items():
                                if op == "$in" and doc[k] not in op_val:
                                    match = False
                                elif op == "$nin" and doc[k] in op_val:
                                    match = False
                                # Add more operators as needed
                        elif doc[k] != v:
                            match = False
                    else:
                        match = False
                
                if match:
                    results.append(doc.copy())
            
            # Simple sort implementation
            if kwargs.get("sort"):
                field, direction = kwargs["sort"]
                reverse = direction < 0
                results.sort(key=lambda x: x.get(field, 0), reverse=reverse)
            
            # Simple limit implementation
            if kwargs.get("limit"):
                results = results[:kwargs["limit"]]
                
            return results
            
        def find_one(self, query=None):
            results = self.find(query)
            return results[0] if results else None
            
        def insert_one(self, document):
            if "_id" not in document:
                document["_id"] = str(self._id_counter)
                self._id_counter += 1
            self.data.append(document)
            return type('obj', (object,), {'inserted_id': document["_id"]})
            
        def insert_many(self, documents):
            for doc in documents:
                self.insert_one(doc)
            return type('obj', (object,), {'inserted_ids': [d.get("_id") for d in documents]})
            
        def update_one(self, query, update, *args, **kwargs):
            for i, doc in enumerate(self.data):
                match = True
                for k, v in query.items():
                    if k in doc and doc[k] != v:
                        match = False
                    elif k not in doc:
                        match = False
                        
                if match:
                    for op, values in update.items():
                        if op == "$set":
                            for field, value in values.items():
                                self.data[i][field] = value
                        elif op == "$push":
                            for field, value in values.items():
                                if field not in self.data[i]:
                                    self.data[i][field] = []
                                self.data[i][field].append(value)
                    break
                    
        def delete_one(self, query):
            for i, doc in enumerate(self.data):
                match = True
                for k, v in query.items():
                    if k in doc and doc[k] != v:
                        match = False
                    elif k not in doc:
                        match = False
                        
                if match:
                    del self.data[i]
                    break
    
    # Create a simple class to mimic MongoDB database behavior
    class MockDatabase:
        def __init__(self):
            self.collections = {}
            
        def __getitem__(self, name):
            if name not in self.collections:
                self.collections[name] = MockCollection(name)
            return self.collections[name]
            
        def list_collection_names(self):
            return list(self.collections.keys())
    
    # Create a mock client
    class MockClient:
        def __init__(self):
            self.db = MockDatabase()
            
        def __getitem__(self, name):
            return self.db
    
    # Create instances
    client = MockClient()
    db = client.db
    
    # Initialize the mock database with sample data
    create_initial_data(db)
    
    return client, db

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
        # Add sample courses with real materials
        sample_courses = [
            {
                "_id": "course_python_basics",
                "title": "Python Programming Basics",
                "description": "An introduction to Python programming language fundamentals with practical examples and exercises.",
                "category": "Computer Science",
                "difficulty": "beginner",
                "topics": ["variables", "data types", "control flow", "functions"],
                "materials": [
                    {
                        "id": "python_w3schools",
                        "title": "Python Tutorial - W3Schools",
                        "type": "url",
                        "url": "https://www.w3schools.com/python/"
                    },
                    {
                        "id": "python_docs",
                        "title": "Python Official Documentation",
                        "type": "url",
                        "url": "https://docs.python.org/3/tutorial/"
                    }
                ],
                "created_at": datetime.now()
            },
            {
                "_id": "course_data_science_intro",
                "title": "Introduction to Data Science",
                "description": "Learn the fundamentals of data science with Python, including data analysis, visualization, and basic machine learning.",
                "category": "Data Science",
                "difficulty": "intermediate",
                "topics": ["data analysis", "visualization", "statistics", "machine learning basics"],
                "materials": [
                    {
                        "id": "data_science_coursera",
                        "title": "Data Science Specialization - Coursera",
                        "type": "url",
                        "url": "https://www.coursera.org/specializations/jhu-data-science"
                    },
                    {
                        "id": "pandas_docs",
                        "title": "Pandas Documentation",
                        "type": "url",
                        "url": "https://pandas.pydata.org/docs/"
                    }
                ],
                "created_at": datetime.now()
            },
            {
                "_id": "course_web_dev",
                "title": "Web Development Fundamentals",
                "description": "Master the basics of web development including HTML, CSS, and JavaScript.",
                "category": "Computer Science",
                "difficulty": "beginner",
                "topics": ["HTML", "CSS", "JavaScript", "Web Design"],
                "materials": [
                    {
                        "id": "mdn_web",
                        "title": "MDN Web Docs",
                        "type": "url",
                        "url": "https://developer.mozilla.org/en-US/docs/Learn"
                    },
                    {
                        "id": "freecodecamp",
                        "title": "FreeCodeCamp Web Development",
                        "type": "url",
                        "url": "https://www.freecodecamp.org/learn/responsive-web-design/"
                    }
                ],
                "created_at": datetime.now()
            },
            {
                "_id": "course_machine_learning",
                "title": "Machine Learning Fundamentals",
                "description": "Learn the core concepts of machine learning and implement them using Python.",
                "category": "Data Science",
                "difficulty": "advanced",
                "topics": ["supervised learning", "unsupervised learning", "neural networks", "deep learning"],
                "materials": [
                    {
                        "id": "ml_coursera",
                        "title": "Machine Learning by Andrew Ng",
                        "type": "url",
                        "url": "https://www.coursera.org/learn/machine-learning"
                    },
                    {
                        "id": "scikit_learn",
                        "title": "Scikit-learn Documentation",
                        "type": "url",
                        "url": "https://scikit-learn.org/stable/"
                    }
                ],
                "created_at": datetime.now()
            }
        ]
        courses_collection.insert_many(sample_courses)
    
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

def enroll_in_course(db, user_id, course_id):
    """Enroll a user in a course"""
    try:
        # Add to progress collection
        progress_collection = db["progress"]
        progress_collection.insert_one({
            "user_id": user_id,
            "course_id": course_id,
            "enrolled_at": datetime.now(),
            "status": "in_progress",
            "progress": 0
        })
        return True
    except Exception as e:
        st.error(f"Failed to enroll in course: {e}")
        return False

def unenroll_from_course(db, user_id, course_id):
    """Remove a user's enrollment from a course"""
    try:
        progress_collection = db["progress"]
        progress_collection.delete_one({
            "user_id": user_id,
            "course_id": course_id
        })
        return True
    except Exception as e:
        st.error(f"Failed to unenroll from course: {e}")
        return False

def update_user_material(db, material_id, updates):
    """Update a user's material with new content"""
    try:
        materials_collection = db["user_materials"]
        updates["last_edited"] = datetime.now()
        materials_collection.update_one(
            {"_id": material_id},
            {"$set": updates}
        )
        return True
    except Exception as e:
        st.error(f"Failed to update material: {e}")
        return False

def update_post_reaction(db, post_id, user_id, reaction_type):
    """Update a post's reaction count and track user reactions"""
    try:
        posts_collection = db["community_posts"]
        
        # Get the current post
        post = posts_collection.find_one({"_id": post_id})
        if not post:
            return False
        
        # Initialize reactions if they don't exist
        if "reactions" not in post:
            post["reactions"] = {}
        
        # Check if user has already reacted
        user_reactions = post.get("user_reactions", {})
        current_reaction = user_reactions.get(user_id)
        
        # If user is removing their reaction
        if current_reaction == reaction_type:
            # Remove the reaction
            posts_collection.update_one(
                {"_id": post_id},
                {
                    "$inc": {f"{reaction_type}s": -1},
                    "$unset": {f"user_reactions.{user_id}": ""}
                }
            )
        else:
            # If user had a different reaction, remove it first
            if current_reaction:
                posts_collection.update_one(
                    {"_id": post_id},
                    {"$inc": {f"{current_reaction}s": -1}}
                )
            
            # Add the new reaction
            posts_collection.update_one(
                {"_id": post_id},
                {
                    "$inc": {f"{reaction_type}s": 1},
                    "$set": {f"user_reactions.{user_id}": reaction_type}
                }
            )
        
        return True
    except Exception as e:
        st.error(f"Failed to update reaction: {e}")
        return False

def delete_material(db, material_id):
    """Delete a material from the database"""
    try:
        materials_collection = db["user_materials"]
        result = materials_collection.delete_one({"_id": material_id})
        if result.deleted_count > 0:
            return True
        return False
    except Exception as e:
        st.error(f"Failed to delete material: {e}")
        return False
