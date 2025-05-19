import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

def display_progress_chart(progress_data):
    """Display a bar chart of course progress"""
    if progress_data.empty:
        st.warning("No progress data available.")
        return
    
    fig = px.bar(
        progress_data,
        x="course",
        y="progress",
        title="Course Progress",
        labels={"course": "Course", "progress": "Progress (%)"},
        color="progress",
        color_continuous_scale="Blues",
        range_color=[0, 100]
    )
    
    fig.update_layout(
        xaxis_title="Course",
        yaxis_title="Progress (%)",
        yaxis_range=[0, 100],
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_score_chart(quiz_data):
    """Display a bar chart of quiz scores"""
    if quiz_data.empty:
        st.warning("No quiz data available.")
        return
    
    fig = px.bar(
        quiz_data,
        x="course",
        y="score",
        title="Recent Quiz Scores",
        labels={"course": "Course", "score": "Score (%)"},
        color="score",
        color_continuous_scale="Greens",
        range_color=[0, 100]
    )
    
    fig.update_layout(
        xaxis_title="Course",
        yaxis_title="Score (%)",
        yaxis_range=[0, 100],
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_summary_metrics(stats):
    """Display summary metrics in a multi-column layout"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Courses Enrolled",
            value=stats["total_courses"]
        )
    
    with col2:
        st.metric(
            label="Average Course Progress",
            value=f"{stats['avg_progress']:.1f}%"
        )
    
    with col3:
        st.metric(
            label="Average Quiz Score",
            value=f"{stats['avg_score']:.1f}%"
        )

def display_radar_chart(skills_data):
    """Display a radar chart of skill levels"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=skills_data["level"],
        theta=skills_data["skill"],
        fill="toself",
        name="Current Skills"
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        title="Skill Assessment",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def format_timestamp(timestamp):
    """Format a timestamp to a readable date string"""
    if isinstance(timestamp, datetime):
        return timestamp.strftime("%b %d, %Y")
    return "Unknown date"

def create_course_card(course, is_enrolled=False):
    """Create a styled card for a course"""
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader(course["title"])
            st.write(course["description"])
            st.caption(f"Category: {course['category']} | Difficulty: {course['difficulty'].capitalize()}")
            
        with col2:
            if is_enrolled:
                st.button("Continue Learning", key=f"continue_{course['_id']}")
            else:
                st.button("Enroll", key=f"enroll_{course['_id']}")
        
        st.markdown("---")

def create_assessment_card(assessment, take_assessment_callback=None):
    """Create a styled card for an assessment"""
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader(assessment["title"])
            st.write(assessment["description"])
            st.caption(f"Questions: {len(assessment['questions'])}")
            
        with col2:
            if take_assessment_callback:
                if st.button("Take Assessment", key=f"take_{assessment['_id']}"):
                    take_assessment_callback(assessment["_id"])
            else:
                st.button("Take Assessment", key=f"take_{assessment['_id']}")
        
        st.markdown("---")

def create_community_post_card(post, user_id="demo_student_id", posts_collection=None, index=0):
    """Create a styled card for a community post with toggleable reactions"""
    with st.container():
        st.subheader(post["title"])
        st.caption(f"Posted by {post['username']} on {format_timestamp(post['created_at'])} | Topic: {post['topic']}")
        st.write(post["content"])
        
        # Track user reactions in session state if not already present
        if "user_reactions" not in st.session_state:
            st.session_state.user_reactions = {}
        
        # Generate a unique key for this post
        reaction_key = f"reaction_{post.get('_id', 'unknown')}"
        
        # Check if user has already reacted to this post
        has_reacted = st.session_state.user_reactions.get(reaction_key, False)
        
        col1, col2 = st.columns([1, 10])
        with col1:
            # Display different button based on reaction status
            if has_reacted:
                # User already liked, clicking will remove the like
                if st.button(f"❤️ {post['likes']} (Liked)", key=f"like_{post.get('_id', 'unknown')}_{index}"):
                    if posts_collection:
                        # Decrement like count
                        posts_collection.update_one(
                            {"_id": post["_id"]},
                            {"$inc": {"likes": -1}}
                        )
                        # Update user reaction status
                        st.session_state.user_reactions[reaction_key] = False
                        st.rerun()
            else:
                # User hasn't liked yet, clicking will add a like
                if st.button(f"🤍 {post['likes']}", key=f"like_{post.get('_id', 'unknown')}_{index}"):
                    if posts_collection:
                        # Increment like count
                        posts_collection.update_one(
                            {"_id": post["_id"]},
                            {"$inc": {"likes": 1}}
                        )
                        # Update user reaction status
                        st.session_state.user_reactions[reaction_key] = True
                        st.rerun()
        
        if post.get("comments"):
            st.write(f"{len(post['comments'])} Comments:")
            for comment in post["comments"]:
                with st.container():
                    st.caption(f"{comment['username']} on {format_timestamp(comment.get('created_at', 'unknown'))}")
                    st.text(comment["content"])
        
        st.markdown("---")

def create_qa_card(question, index):
    """Create a card for displaying a Q&A question"""
    with st.container():
        st.subheader(question.get("title", "Untitled Question"))
        st.write(question.get("content", ""))
        st.caption(f"Topic: {question.get('topic', 'Unspecified')}")
        st.caption(f"Posted by {question.get('username', 'Anonymous')} on {format_timestamp(question.get('created_at'))}")
        if question.get("answered"):
            st.markdown("### Answer:")
            st.markdown(question.get("ai_answer", ""))
        else:
            st.info("This question is waiting for an answer.")
        
        st.divider()
