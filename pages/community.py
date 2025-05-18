import streamlit as st
from database import add_community_post
from .utils import create_community_post_card, format_timestamp

def show_community(db):
    """Display the community page"""
    st.title("👥 Community")
    
    # Get the current user ID and username
    user_id = st.session_state.get("user_id", "demo_student_id")
    username = st.session_state.get("username", "Demo Student")
    
    # Tabs for Posts and Create Post
    tab1, tab2 = st.tabs(["Posts", "Create Post"])
    
    with tab1:
        show_community_posts(db)
    
    with tab2:
        create_post(db, user_id, username)

def show_community_posts(db):
    """Show community posts with filtering options"""
    st.header("Community Posts")
    
    # Filtering options
    col1, col2 = st.columns(2)
    
    with col1:
        # Topic filter
        topics = ["All", "General", "Computer Science", "Data Science", "Mathematics", "Science", "Language Learning", "Study Tips"]
        selected_topic = st.selectbox("Filter by Topic", topics)
    
    with col2:
        # Sort options
        sort_options = ["Newest", "Most Liked"]
        sort_by = st.selectbox("Sort by", sort_options)
    
    # Search box
    search_query = st.text_input("Search Posts", "")
    
    # Query the database for posts
    posts_collection = db["community_posts"]
    query = {}
    
    if selected_topic != "All":
        query["topic"] = selected_topic
    
    if search_query:
        query["$or"] = [
            {"title": {"$regex": search_query, "$options": "i"}},
            {"content": {"$regex": search_query, "$options": "i"}}
        ]
    
    # Sort the posts
    if sort_by == "Newest":
        posts = list(posts_collection.find(query).sort("created_at", -1))
    else:  # Most Liked
        posts = list(posts_collection.find(query).sort("likes", -1))
    
    if posts:
        # Display posts
        for post in posts:
            create_community_post_card(post)
            
            # Comment form (displayed under each post)
            with st.expander("Add a comment"):
                comment_content = st.text_area("Your comment", key=f"comment_{post.get('_id', 'unknown')}")
                
                if st.button("Submit", key=f"submit_comment_{post.get('_id', 'unknown')}"):
                    if comment_content:
                        # Add the comment to the post
                        user_id = st.session_state.get("user_id", "demo_student_id")
                        username = st.session_state.get("username", "Demo Student")
                        
                        comment = {
                            "user_id": user_id,
                            "username": username,
                            "content": comment_content,
                            "created_at": st.session_state.get("now", None)
                        }
                        
                        posts_collection.update_one(
                            {"_id": post["_id"]},
                            {"$push": {"comments": comment}}
                        )
                        
                        st.success("Comment added!")
                        st.rerun()
                    else:
                        st.warning("Please enter a comment.")
    else:
        st.info("No posts found matching your criteria.")

def create_post(db, user_id, username):
    """Interface for creating a new community post"""
    st.header("Create a New Post")
    
    # Post form
    title = st.text_input("Title")
    content = st.text_area("Content", height=150)
    
    # Topic selection
    topics = ["General", "Computer Science", "Data Science", "Mathematics", "Science", "Language Learning", "Study Tips"]
    topic = st.selectbox("Topic", topics)
    
    # Submit button
    if st.button("Post"):
        if title and content:
            # Add the post to the database
            add_community_post(db, user_id, username, title, content, topic)
            
            st.success("Post created successfully!")
            st.rerun()
        else:
            st.warning("Please fill in both title and content fields.")
    
    # Display posting guidelines
    with st.expander("Community Guidelines"):
        st.markdown("""
        ### Community Guidelines
        
        1. **Be Respectful** - Treat others with respect and kindness.
        
        2. **Stay On Topic** - Posts should be relevant to learning and education.
        
        3. **No Plagiarism** - Always cite your sources and do not copy others' work.
        
        4. **No Spam** - Avoid posting repetitive or promotional content.
        
        5. **Be Constructive** - Provide helpful feedback and meaningful contributions.
        
        6. **Protect Privacy** - Do not share personal information about yourself or others.
        
        7. **Follow Academic Integrity** - Do not share answers to assignments or exams.
        
        Failure to follow these guidelines may result in post removal or account restrictions.
        """)
