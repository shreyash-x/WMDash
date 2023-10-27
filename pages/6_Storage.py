import streamlit as st
import os
import pandas as pd
import plost
import plotly.express as px
import json
import datetime
# Data Loading
import data.loadMessages as loadMessages
import data.loadFiles as loadFiles
import data.loadParticipants as loadParticipants
participants_data = loadParticipants.ParticipantsData()
messageData = loadMessages.MessageData()

# Downloaded Data Path
dataDir = '/mnt/storage/kg766/WhatsappMonitorData/'

# # Function that returns directory size in MBs
# def getDirectorySize(directory):
#     total_size = 0
#     date_map = {}
#     for dirpath, dirnames, filenames in os.walk(directory):
#         for f in filenames:
#             if not f.endswith('.json'):
#                 fp = os.path.join(dirpath, f)
#                 json_file_path = os.path.splitext(fp)[0] + '.json'
                
#                 if os.path.exists(json_file_path):
#                     # Load and extract date from the JSON file
#                     with open(json_file_path, 'r') as json_file:
#                         json_data = json.load(json_file)
#                         if 'message' in json_data and 'timestamp' in json_data['message']:
#                             ts = json_data['message']['timestamp']
#                             ts = pd.to_datetime(ts,unit='s')
#                             date = ts.strftime("%d-%m-%Y")
#                             size = os.path.getsize(fp) / (1024*1024)
#                             total_size += size
#                             date_map[date] = date_map.get(date, 0) + size
#     return total_size, date_map
# Function that returns directory size in MBs
def getDirectorySize(directory):
    total_size = 0
    date_map = {}
    for dirpath, dirnames, filenames in os.walk(directory):
        for f in filenames:
            if not f.endswith('.json'):
                fp = os.path.join(dirpath, f)
                creation_time = os.path.getctime(fp)
                # Convert creation time to a human-readable date format
                creation_date = datetime.datetime.fromtimestamp(creation_time).strftime('%Y-%m-%d')
                size = os.path.getsize(fp) / (1024*1024)
                total_size += size
                date_map[creation_date] = date_map.get(creation_date, 0) + size
    return total_size, date_map

dataMapping = {}
TSMap = {}

# Sidebar
st.sidebar.title('WM Dashboard')

# Radio button to select find by : Username or Surveyor
select_all_users = st.sidebar.checkbox('Select all users')
if select_all_users:
    userNames = messageData.getUserNames()
    for user in userNames:
            chatNames = messageData.getChatNames(user)
            message_ids = messageData.getMessageIds(user, chatNames)
            dataMapping[user] = [dataDir + 'downloaded-media/' + user.split('(')[0].strip() + '-' + message_id for message_id in message_ids]
else:
    find_by = st.sidebar.radio('Find by', ['User', 'Surveyor'])

    if find_by == 'User':
        st.sidebar.subheader('User Name')
        userNames = messageData.getUserNames()
        userName = st.sidebar.selectbox('Participant', userNames)

        # Checkbox to select all chats
        select_all_chats = st.sidebar.checkbox('Select all chats')

        # Multi select box to select chats
        chatNames = messageData.getChatNames(userName)
        if select_all_chats:
            default_chatNames = chatNames
        else:
            default_chatNames = []
        st.sidebar.subheader('Chat Name')
        chatName = st.sidebar.multiselect('Chat', chatNames, default=default_chatNames)
        message_ids = messageData.getMessageIds(userName, chatName)
        
        dataMapping[userName] = [dataDir + 'downloaded-media/' + userName.split('(')[0].strip() + '-' + message_id for message_id in message_ids]

    elif find_by == 'Surveyor':
        st.sidebar.subheader('Surveyor')
        # multi select box for selecting multiple surveyors
        surveyors = st.sidebar.multiselect('Select surveyors', participants_data.getSurveyors())
        userNames = participants_data.getParticipantsBySurveyors(surveyors)
        for user in userNames:
            chatNames = messageData.getChatNames(user)
            message_ids = messageData.getMessageIds(user, chatNames)
            dataMapping[user] = [dataDir + 'downloaded-media/' + user.split('(')[0].strip() + '-' + message_id for message_id in message_ids]



st.sidebar.markdown('''
---
Data Visualizer for WhatsappExplorer.
''')

# Page
# Show filename and filesize of all message files
st.markdown('## Downloaded Media')
if (len(dataMapping.keys())==0):
    st.markdown("Empty Set")
else:
    Total_Size = 0
    Calculated_Size = []
    #  1st Jan 1970 is default date
    default_date = pd.to_datetime('1970-01-01')
    dojs = participants_data.getDOJS(dataMapping.keys())
    for user, data in dataMapping.items():
        User_Size = 0
        for path in data:
            if os.path.exists(path):
                dir_size, ts_map = getDirectorySize(path)
                User_Size += dir_size
                Total_Size += dir_size
                
                for date in ts_map:
                    if date in TSMap:
                        TSMap[date] += ts_map[date]
                    else:
                        TSMap[date] = ts_map[date]
        Calculated_Size.append({
            'User': user,
            'Size': User_Size,
            'DOJ': dojs[user] if user in dojs else default_date,
        })



    dataSize_df = pd.DataFrame(Calculated_Size)

    #  Plot Size of data per user using bar chart
    st.markdown('### Data Usage Per User in MBs')
    fig = px.bar(dataSize_df, x='User', y='Size')
    fig.update_layout(
        xaxis_title="User",
        yaxis_title="Size (MBs)",
        font=dict(
            size=12,
        )
    )
    st.plotly_chart(fig)

    # Plot Data Usage per DOJ, where DOJ is reduced to date only
    st.markdown("## Based on DOJ (Size in GBs)")
    st.markdown('### Bar Chart')
    dataSize_df['DOJ'] = dataSize_df['DOJ'].dt.date
    dataSize_df['Size'] = round(dataSize_df['Size']/1024,2)
    # Add count of users per DOJ
    # Group by 'DOJ' and aggregate the count of users and sum of 'Size'
    result = dataSize_df.groupby('DOJ').agg({'User': 'count', 'Size': 'sum'}).reset_index()
    fig = px.bar(result, x='DOJ', y='Size', text='User',
             labels={'DOJ': 'Date of Joining', 'Size': 'Total Size', 'User': 'User Count'})
    fig.update_xaxes(type='category')  # Ensure x-axis treats 'DOJ' as a category
    fig.update_traces(texttemplate='%{text}', textposition='outside')  # Add user count as text on top of bars
    st.plotly_chart(fig)
    
    # Cumulative Sum of Data Usage per DOJ
    st.markdown('### Cumulative Data Usage')
    result['cumsum'] = result['Size'].cumsum()
    fig = px.line(result, x='DOJ', y='cumsum',
             labels={'DOJ': 'Date of Joining', 'cumsum': 'Total Size'})
    fig.update_xaxes(type='category')
    st.plotly_chart(fig)
    
    
    # Data usage based on media sent date
    st.markdown("## Based on date downloaded (Size in GBs)")
    TSMap = dict(sorted(TSMap.items()))
    # Create a DataFrame for Plotly Express
    TS_df = pd.DataFrame({'Date': list(TSMap.keys()), 'Size': list(TSMap.values())})
    TS_df['Size'] = round(TS_df['Size']/1024,2)
    # Calculate cumulative size
    TS_df['Cumulative Size'] = TS_df['Size'].cumsum()

    # Display a bar chart using Plotly Express
    st.markdown("### Bar Chart")
    bar_chart = px.bar(TS_df, x='Date', y='Size', title='Size Used per Date')
    st.plotly_chart(bar_chart)

    # Display a line chart using Plotly Express
    st.markdown("### Cummulative Size Usage")
    line_chart = px.line(TS_df, x='Date', y='Cumulative Size', title='Cumulative Size')
    st.plotly_chart(line_chart)

    Total_Size = round(Total_Size/1024, 2)
    st.markdown('**Total Size** : ' + str(Total_Size) + ' GB')
