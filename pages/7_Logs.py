import streamlit as st
import pandas as pd
import re
import plost
import plotly.express as px
import subprocess

import data.loadParticipants as loadParticipants
participants_data = loadParticipants.ParticipantsData()

# Function to read the last N lines of the log file
def read_last_n_lines(log_file, n):
    log_entries = []
    with open(log_file, 'r') as file:
        lines = file.readlines()
        last_n_lines = lines[-n:]
        for line in last_n_lines:
            match = re.match(r'\[(.*?)\] (.*?)\s*:\s*(.*)', line)
            if match:
                timestamp = match.group(1)
                username = match.group(2)
                message = match.group(3)
                log_entries.append({'Timestamp': timestamp, 'Username': username, 'Message': message})
            else:
                log_entries.append({'Timestamp': 'N/A', 'Username': 'N/A', 'Message': line.strip()})
    return log_entries[::-1]

def read_and_search_log(log_file, search_term):
    result = []
    with open(log_file, 'r') as file:
        for line in file:
            if search_term in line:
                match = re.match(r'\[(.*?)\] (.*?)\s*:\s*(.*)', line)
                if match:
                    timestamp = match.group(1)
                    username = match.group(2)
                    message = match.group(3)
                    result.append({'Timestamp': timestamp, 'Username': username, 'Message': message})
                else:
                    result.append({'Timestamp': 'N/A', 'Username': 'N/A', 'Message': line.strip()})
    return result[::-1]


st.title("Log Viewer")
log_file = "../api/whatsappWebApi/client-logs.txt"  # Replace with the actual path to your log file
default_num_lines = 1000

st.sidebar.header("Search")
search_term = st.sidebar.text_input("Enter a search term")

num_lines = st.sidebar.slider("Number of lines to display", 1, 5000, default_num_lines)

if search_term:
    st.subheader("Search Results")
    log_contents = read_and_search_log(log_file, search_term)
    df = pd.DataFrame(log_contents)
    st.write(
        df.style.set_table_styles([{'selector': 'table', 'props': [('width', '100%')]}]),
        use_container_width=True
    )
else:
    st.subheader("Log File Contents")
    log_contents = read_last_n_lines(log_file, num_lines)
    df = pd.DataFrame(log_contents)
    st.write(
        df.style.set_table_styles([{'selector': 'table', 'props': [('width', '100%')]}]),
        use_container_width=True
    )

st.markdown("### Client Status")
statusData = participants_data.getClientStatus()
status_df = pd.DataFrame(statusData).sort_values("Status")
grouped_df = status_df.groupby('Status').count().reset_index()
st.write(status_df)
# create a pie chart
fig = px.pie(grouped_df, values='Name', names='Status', title='Distribution of status', labels={'Name':'Count', 'Status': "Status"})
st.plotly_chart(fig, use_container_width=True)


# st.markdown('### Special Commands: Use with caution')
# if st.button('Restart Server'):
#     proc = subprocess.Popen(["pm2 status"], stdout=subprocess.PIPE, shell=True)
#     (out, err) = proc.communicate()
#     st.markdown('Result')
#     ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
#     out = ansi_escape.sub('', out.decode('utf-8'))
#     st.write(out)