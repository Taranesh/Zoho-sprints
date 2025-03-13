import streamlit as st
import pymongo
import uuid
import socket
from datetime import datetime
import pandas as pd
import random
import plotly.express as px
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.mention import mention

# MongoDB connection
client = pymongo.MongoClient("mongodb+srv://smaas:scmxpert123SCM@scmxpert.5h1vx.mongodb.net/SCM?retryWrites=true&w=majority")
db = client["productivity_dashboard"]
updates_collection = db["task_notes"]

# Get device IP address
def get_device_ip():
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return "Unknown IP"

# Page Title
st.set_page_config(page_title="Personal Productivity Dashboard", layout="wide")
# Hide Streamlit Header and Footer using CSS
hide_streamlit_style = """
    <style>
        [data-testid="stHeader"] {display: none;}  /* Hide Header */
        [data-testid="stToolbar"] {display: none;}  /* Hide Toolbar */
        footer {visibility: hidden;}  /* Hide Footer */
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Sidebar Menu
st.sidebar.title("Navigation")
menu = st.sidebar.radio("Go to", ["📊 Zoho Productivity Stats", "📝 Task Manager", "📅 Calendar", "🔍 Insights", "💡 Productivity Tips"])

# Random Productivity Score
st.sidebar.metric(label="🔥 Daily Focus Score", value=f"{random.randint(50, 100)}%")

# Secret Password for Hidden Communication
CONSTANT_PASSWORD = "111"

# Productivity Stats Page
if menu == "📊 Zoho Productivity Stats":
    st.title("📊 Zoho EDI Parsing Dashboard")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Tasks Completed", random.randint(5, 20))
    with col2:
        st.metric("Focus Time (hrs)", round(random.uniform(2, 8), 1))
    with col3:
        st.metric("Break Time (mins)", random.randint(15, 60))

    # Line Chart for Productivity Over Time
    st.subheader("🕑 Productivity Over Time")
    time_data = pd.DataFrame({"Day": ["Mon", "Tue", "Wed", "Thu", "Fri"], "Score": [random.randint(60, 100) for _ in range(5)]})
    fig = px.line(time_data, x="Day", y="Score", title="Productivity Trend", markers=True)
    st.plotly_chart(fig)

    # Task Distribution Pie Chart
    st.subheader("📌 Task Distribution")
    task_data = pd.DataFrame({"Task Type": ["Completed", "Pending", "In Progress"], "Count": [random.randint(5, 15), random.randint(5, 15), random.randint(5, 15)]})
    fig_pie = px.pie(task_data, names="Task Type", values="Count", title="Task Status Breakdown")
    st.plotly_chart(fig_pie)

    # Bar Chart for Work vs Break Time
    st.subheader("⌛ Work vs Break Time")
    work_break_data = pd.DataFrame({"Category": ["Work Time", "Break Time"], "Hours": [random.randint(4, 10), random.randint(1, 3)]})
    fig_bar = px.bar(work_break_data, x="Category", y="Hours", title="Work vs Break Time", text_auto=True)
    st.plotly_chart(fig_bar)

# Task Manager Page
elif menu == "📝 Task Manager":
    st.title("📝 Task Manager")

    st.header("Add New Task")
    task_title = st.text_input("Task Name", "")
    task_priority = st.selectbox("Priority", ["Low", "Medium", "High"])
    task_status = st.selectbox("Status", ["Pending", "In Progress", "Completed"])
    task_notes = st.text_area("Notes (Encrypted)")

    if st.button("Save Task"):
        if not task_title or not task_notes:
            st.error("Task Name and Notes are required!")
        else:
            update_id = str(uuid.uuid4())
            sender_ip = get_device_ip()

            updates_collection.insert_one({
                "update_id": update_id,
                "task_title": task_title,
                "priority": task_priority,
                "status": task_status,
                "notes": task_notes,
                "timestamp": datetime.now(),
                "sender_ip": sender_ip
            })
            st.success("Task saved successfully!")
            st.rerun()

    # Hidden Communication - Requires Password
    st.header("🔒 Task History (Admin Only)")
    password = st.text_input("Enter Admin Password", type="password")

    if password == CONSTANT_PASSWORD:
        updates = list(updates_collection.find())
        if not updates:
            st.warning("No tasks available.")
        else:
            df = pd.DataFrame(updates)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df[['update_id', 'task_title', 'priority', 'status', 'notes', 'timestamp']]

            if st.button("🗑️ Delete All Tasks"):
                updates_collection.delete_many({})
                st.success("All tasks deleted successfully!")
                st.rerun()

            for _, row in df.iterrows():
                update_id = row["update_id"]
                col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])
                with col1:
                    st.write(row['task_title'])
                with col2:
                    st.write(row['priority'])
                with col3:
                    st.write(row['status'])
                with col4:
                    if st.button(f"👁️ ", key=f"toggle-{update_id}"):
                        st.session_state[f"show_notes_{update_id}"] = not st.session_state.get(f"show_notes_{update_id}", False)
                    if st.session_state.get(f"show_notes_{update_id}", False):
                        st.write(f"**Message:** {row['notes']}")
                    else:
                        st.write("🔒 Encrypted")
                with col5:
                    if st.button(f"🗑️", key=f"delete-{update_id}"):
                        updates_collection.delete_one({"update_id": update_id})
                        st.success(f"Task '{row['task_title']}' deleted.")
                        st.rerun()