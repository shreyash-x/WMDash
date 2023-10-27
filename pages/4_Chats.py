import streamlit as st
import pandas as pd
import plost
import plotly.express as px
import datetime
# Data Loading
import data.loadChatusers as loadChatusers
chatData = loadChatusers.ChatuserData()

# Sidebar
st.sidebar.title('WM Dashboard')
st.sidebar.subheader('User Name')
userNames = chatData.getUserNames()
userName = st.sidebar.selectbox('Participant', userNames)

st.sidebar.markdown('''
---
Data Visualizer for WhatsappExplorer.
''')

# Page
st.markdown('### Selected User Chats')
chatUsers = chatData.getChatusers(userName)
if chatUsers is None or len(chatUsers) == 0:
    st.markdown('Please select a user from the sidebar.')
else:
    st.dataframe(chatUsers)