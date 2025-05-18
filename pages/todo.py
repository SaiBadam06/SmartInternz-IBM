import streamlit as st
from datetime import datetime, timedelta

def show_todo(db):
    """Display the todo list page"""
    st.title("📋 Task Planner")
    
    # Get the current user ID
    user_id = st.session_state.get("user_id", "demo_student_id")
    
    # Create tabs for Today's Tasks, Weekly Planner, and Task History
    tab1, tab2, tab3 = st.tabs(["Today's Tasks", "Weekly Planner", "Task History"])
    
    with tab1:
        show_daily_tasks(db, user_id)
    
    with tab2:
        show_weekly_planner(db, user_id)
        
    with tab3:
        show_task_history(db, user_id)

def show_daily_tasks(db, user_id):
    """Show today's tasks and allow adding new tasks"""
    st.header("Today's Tasks")
    
    # Get today's date and format it
    today = datetime.now().strftime("%Y-%m-%d")
    st.subheader(f"Date: {datetime.now().strftime('%A, %B %d, %Y')}")
    
    # Add a new task form
    with st.form("add_task_form"):
        task_name = st.text_input("Task Name", placeholder="Enter a new task...")
        
        col1, col2 = st.columns(2)
        with col1:
            priority = st.select_slider("Priority", options=["Low", "Medium", "High"], value="Medium")
        with col2:
            time_estimate = st.number_input("Time Estimate (minutes)", min_value=5, max_value=480, value=30, step=5)
        
        task_type = st.selectbox(
            "Task Type", 
            ["Study", "Assignment", "Reading", "Practice", "Project", "Exam Preparation", "Other"]
        )
        
        notes = st.text_area("Notes (Optional)", placeholder="Add any additional notes here...")
        submitted = st.form_submit_button("Add Task")
    
    if submitted:
        if task_name:
            # Add task to database
            tasks_collection = db["user_tasks"]
            
            new_task = {
                "user_id": user_id,
                "name": task_name,
                "priority": priority,
                "time_estimate": time_estimate,
                "task_type": task_type,
                "notes": notes,
                "date": today,
                "completed": False,
                "created_at": datetime.now()
            }
            
            tasks_collection.insert_one(new_task)
            st.toast(f"Task '{task_name}' added for today", icon="✅")
            st.rerun()
        else:
            st.toast("Please enter a task name", icon="⚠️")
    
    # Display today's tasks
    tasks_collection = db["user_tasks"]
    today_tasks = list(tasks_collection.find({
        "user_id": user_id,
        "date": today
    }))
    
    if today_tasks:
        # Group tasks by completion status
        pending_tasks = [t for t in today_tasks if not t.get("completed", False)]
        completed_tasks = [t for t in today_tasks if t.get("completed", False)]
        
        # Show pending tasks
        if pending_tasks:
            st.subheader("Pending Tasks")
            for i, task in enumerate(pending_tasks):
                col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
                
                with col1:
                    if st.checkbox("", key=f"check_{task.get('_id', i)}", value=False):
                        # Mark as completed
                        tasks_collection.update_one(
                            {"_id": task["_id"]},
                            {"$set": {"completed": True}}
                        )
                        st.toast(f"Task '{task['name']}' completed!", icon="🎉")
                        st.rerun()
                
                with col2:
                    priority_color = {
                        "Low": "blue",
                        "Medium": "orange",
                        "High": "red"
                    }.get(task["priority"], "gray")
                    
                    st.markdown(
                        f"<div style='display:flex;align-items:center;'>"
                        f"<span style='color:{priority_color};font-weight:bold;margin-right:10px;'>●</span>"
                        f"<span style='font-weight:bold;'>{task['name']}</span>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                    st.caption(f"{task['task_type']} • {task['time_estimate']} mins")
                    if task.get("notes"):
                        with st.expander("Notes"):
                            st.write(task["notes"])
                
                with col3:
                    if st.button("🗑️", key=f"delete_{task.get('_id', i)}"):
                        tasks_collection.delete_one({"_id": task["_id"]})
                        st.toast("Task deleted", icon="🗑️")
                        st.rerun()
                
                st.divider()
        
        # Show completed tasks in an expander
        if completed_tasks:
            with st.expander(f"Completed Tasks ({len(completed_tasks)})"):
                for i, task in enumerate(completed_tasks):
                    st.markdown(f"~~**{task['name']}**~~")
                    st.caption(f"{task['task_type']} • {task['time_estimate']} mins")
                    if i < len(completed_tasks) - 1:
                        st.divider()
    else:
        st.info("No tasks for today. Add a task to get started!")
    
    # Show task summary
    if today_tasks:
        st.subheader("Today's Summary")
        
        completed_count = len([t for t in today_tasks if t.get("completed", False)])
        total_count = len(today_tasks)
        completion_rate = (completed_count / total_count) * 100 if total_count > 0 else 0
        
        # Display progress bar
        st.progress(completion_rate / 100)
        st.write(f"Completed: {completed_count}/{total_count} tasks ({completion_rate:.0f}%)")
        
        # Calculate estimated time remaining
        remaining_time = sum([t.get("time_estimate", 0) for t in today_tasks if not t.get("completed", False)])
        if remaining_time > 0:
            st.write(f"Estimated time remaining: {remaining_time} minutes")

def show_weekly_planner(db, user_id):
    """Show and manage weekly task planning"""
    st.header("Weekly Planner")
    
    # Get the start of the current week (Monday)
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    
    # Create date objects for the week
    week_dates = [start_of_week + timedelta(days=i) for i in range(7)]
    week_date_strs = [d.strftime("%Y-%m-%d") for d in week_dates]
    
    # Display the week dates and allow user to select a day
    st.subheader(f"Week of {start_of_week.strftime('%B %d, %Y')}")
    
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    selected_day_idx = st.selectbox(
        "Select a day to plan",
        options=range(7),
        format_func=lambda i: f"{day_names[i]} ({week_dates[i].strftime('%m/%d')})"
    )
    
    selected_date = week_dates[selected_day_idx]
    selected_date_str = selected_date.strftime("%Y-%m-%d")
    
    # Form to add a task for the selected day
    with st.form(f"plan_task_form_{selected_day_idx}"):
        st.subheader(f"Add task for {day_names[selected_day_idx]}")
        
        task_name = st.text_input("Task Name", placeholder="Enter a new task...")
        
        col1, col2 = st.columns(2)
        with col1:
            priority = st.select_slider("Priority", options=["Low", "Medium", "High"], value="Medium")
        with col2:
            time_estimate = st.number_input("Time Estimate (minutes)", min_value=5, max_value=480, value=30, step=5)
        
        task_type = st.selectbox(
            "Task Type", 
            ["Study", "Assignment", "Reading", "Practice", "Project", "Exam Preparation", "Other"]
        )
        
        notes = st.text_area("Notes (Optional)", placeholder="Add any additional notes here...")
        submitted = st.form_submit_button("Add to Planner")
    
    if submitted:
        if task_name:
            # Add task to database
            tasks_collection = db["user_tasks"]
            
            new_task = {
                "user_id": user_id,
                "name": task_name,
                "priority": priority,
                "time_estimate": time_estimate,
                "task_type": task_type,
                "notes": notes,
                "date": selected_date_str,
                "completed": False,
                "created_at": datetime.now()
            }
            
            tasks_collection.insert_one(new_task)
            st.toast(f"Task '{task_name}' added for {day_names[selected_day_idx]}", icon="✅")
            st.rerun()
        else:
            st.toast("Please enter a task name", icon="⚠️")
    
    # Display weekly overview
    st.subheader("Weekly Overview")
    
    # Get all tasks for the week
    tasks_collection = db["user_tasks"]
    week_tasks = list(tasks_collection.find({
        "user_id": user_id,
        "date": {"$in": week_date_strs}
    }))
    
    # Group tasks by day
    tasks_by_day = {day_str: [] for day_str in week_date_strs}
    for task in week_tasks:
        tasks_by_day[task["date"]].append(task)
    
    # Create columns for each day
    cols = st.columns(7)
    
    for i, (col, date, date_str) in enumerate(zip(cols, week_dates, week_date_strs)):
        with col:
            st.markdown(f"**{day_names[i][:3]}**")
            st.caption(date.strftime("%m/%d"))
            
            day_tasks = tasks_by_day[date_str]
            completed = sum(1 for t in day_tasks if t.get("completed", False))
            total = len(day_tasks)
            
            if total > 0:
                st.markdown(f"{completed}/{total} tasks")
                # Small progress indicator
                st.progress((completed/total) if total > 0 else 0)
            else:
                st.markdown("No tasks")

def show_task_history(db, user_id):
    """Show completed tasks history and analytics"""
    st.header("Task History & Analytics")
    
    # Get all tasks for the user
    tasks_collection = db["user_tasks"]
    all_tasks = list(tasks_collection.find({"user_id": user_id}))
    
    if not all_tasks:
        st.info("No task history available. Start adding tasks to see analytics.")
        return
    
    # Filter for completed tasks
    completed_tasks = [t for t in all_tasks if t.get("completed", False)]
    
    # Basic statistics
    st.subheader("Task Completion Stats")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        total_completed = len(completed_tasks)
        st.metric("Total Completed", total_completed)
    
    with col2:
        completion_rate = (len(completed_tasks) / len(all_tasks)) * 100 if len(all_tasks) > 0 else 0
        st.metric("Completion Rate", f"{completion_rate:.1f}%")
    
    with col3:
        if completed_tasks:
            avg_time = sum(t.get("time_estimate", 0) for t in completed_tasks) / len(completed_tasks)
            st.metric("Avg. Task Time", f"{avg_time:.0f} mins")
        else:
            st.metric("Avg. Task Time", "N/A")
    
    # Display recent completed tasks
    st.subheader("Recently Completed Tasks")
    
    # Sort by completion time (we'll use the _id as a proxy for time if needed)
    sorted_completed = sorted(completed_tasks, key=lambda x: x.get("_id", ""), reverse=True)[:10]
    
    if sorted_completed:
        for task in sorted_completed:
            with st.container():
                col1, col2 = st.columns([0.7, 0.3])
                with col1:
                    st.markdown(f"**{task['name']}**")
                    st.caption(f"{task['task_type']} • {task['time_estimate']} mins • {task['priority']} Priority")
                
                with col2:
                    task_date = datetime.strptime(task["date"], "%Y-%m-%d").strftime("%b %d")
                    st.markdown(f"**{task_date}**")
                
                st.divider()
    else:
        st.info("No completed tasks yet.")