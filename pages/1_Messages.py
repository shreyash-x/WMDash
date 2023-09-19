import streamlit as st
import pandas as pd
import plost
import plotly.express as px
import datetime
# Data Loading
import data.loadMessages as loadMessages
messageData = loadMessages.MessageData()

# Sidebar
st.sidebar.title('WM Dashboard')
st.sidebar.subheader('User Name')
userNames = messageData.getUserNames()
userName = st.sidebar.selectbox('Participant', userNames)

st.sidebar.subheader('Chat Name')
chatNames = messageData.getChatNames(userName)
chatName = st.sidebar.selectbox('Chat', chatNames)

st.sidebar.subheader('Date Range')
start_date = st.sidebar.date_input('Start date', value=pd.to_datetime('2020-01-01'))
end_date = st.sidebar.date_input('End date', value=datetime.datetime.now())
if start_date > end_date:
    st.sidebar.error('Error: End date must fall after start date.')

st.sidebar.markdown('''
---
Data Visualizer for WhatsappExplorer.
''')

# Page
st.markdown('### Selected User Message Stats')
messages = messageData.getMessageCount(userName)
if messages is None or len(messages) == 0:
    st.markdown('Please select a user from the sidebar.')
else:
    st.dataframe(messages)

st.markdown('### Selected chat messages')
messages = messageData.getChatMessages(userName, chatName)
if messages is None or len(messages) == 0:
    st.markdown('Please select a chat from the sidebar.')
else:
    message_df = pd.DataFrame(messages)
    # display only few columns
    message_df = message_df[['timestamp', 'body', 'type', 'mediaDownloaded', 'isAnonymized']]
    message_df['timestamp'] = pd.to_datetime(message_df['timestamp'], unit='s')
    message_df = message_df[(message_df['timestamp'].dt.date >= start_date) & (message_df['timestamp'].dt.date <= end_date)]
    message_df = message_df.set_index('timestamp')
    message_df = message_df.sort_index()
    st.write(message_df)

    # Plot frequency of messages per day
    st.markdown('### Messages per day')
    freq_message_df = message_df.copy()
    freq_message_df['date'] = freq_message_df.index.date
    freq_message_df = freq_message_df.groupby('date').count()
    freq_message_df = freq_message_df[['body']]
    freq_message_df = freq_message_df.rename(columns={'body': 'count'})
    # set all y ticks as integers in plot
    st.line_chart(freq_message_df, height=300)