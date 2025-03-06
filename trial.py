import streamlit as st
import pymongo
import uuid
import socket
from datetime import datetime
import pandas as pd

# MongoDB connection
client = pymongo.MongoClient("mongodb+srv://smaas:scmxpert123SCM@scmxpert.5h1vx.mongodb.net/SCM?retryWrites=true&w=majority")
db = client["project_updates"]
updates_collection = db["updates"]

# Constant password
CONSTANT_PASSWORD = "111"

# Get device IP address
def get_device_ip():
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return "Unknown IP"

# Layout
st.title("Real-Time Project Update Tracker")

# Task Submission Form
st.header("Submit Task Update")

contributor_name = st.text_input("Contributor Name", "")
task_title = st.text_input("Task Title", "")

task_type = st.selectbox("Task Type", ["Bug Fix", "Feature Update", "Code Review", "Documentation"])
priority = st.selectbox("Priority", ["Low", "Medium", "High"])
status = st.selectbox("Status", ["In Progress", "Completed", "On Hold"])
task_details = st.text_area("Task Details", "")

if st.button("Submit Update"):
    if not (contributor_name and task_title and task_details):
        st.error("All fields are required!")
    else:
        update_id = str(uuid.uuid4())
        sender_ip = get_device_ip()
        
        updates_collection.insert_one({
            "update_id": update_id,
            "contributor": contributor_name,
            "task_title": task_title,
            "task_type": task_type,
            "priority": priority,
            "status": status,
            "details": task_details,
            "timestamp": datetime.now(),
            "sender_ip": sender_ip
        })
        st.success("Task update submitted successfully!")

# Retrieve Updates - Show Automatically if Password is Correct
st.header("View Task Updates")
password = st.text_input("Enter Admin Password", type="password")

if password == CONSTANT_PASSWORD:  # Auto-show table when the password is correct
    updates = list(updates_collection.find())

    if not updates:
        st.warning("No task updates available.")
    else:
        df = pd.DataFrame(updates)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df[['update_id', 'contributor', 'task_title', 'task_type', 'priority', 'status', 'details', 'timestamp']]

        # Display updates in table format
        st.write("### Task Updates")
        for index, row in df.iterrows():
            col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([1, 2, 2, 2, 1, 1, 3, 1])
            
            with col1:
                st.write(row['update_id'])
            with col2:
                st.write(row['contributor'])
            with col3:
                st.write(row['task_title'])
            with col4:
                st.write(row['task_type'])
            with col5:
                st.write(row['priority'])
            with col6:
                st.write(row['status'])
            with col7:
                # Show encrypted text, reveal on hover
                encrypted_message = "🔒 Encrypted"
                st.markdown(f'<div title="{row["details"]}">{encrypted_message}</div>', unsafe_allow_html=True)
            
            with col8:
                # Delete specific update
                if st.button("❌", key=f"delete-{index}"):
                    updates_collection.delete_one({"update_id": row["update_id"]})
                    st.success(f"Update '{row['task_title']}' deleted.")
                    st.rerun()

        # Delete all updates option
        if st.button("Clear All Updates"):
            if st.checkbox("Are you sure you want to delete all updates?"):
                updates_collection.delete_many({})
                st.success("All updates cleared.")
                st.rerun()
