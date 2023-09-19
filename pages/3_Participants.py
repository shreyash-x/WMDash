import streamlit as st
import pandas as pd
import plost
import plotly.express as px
import datetime
# Data Loading
import data.loadParticipants as loadParticipants
participants_data = loadParticipants.ParticipantsData()

# Sidebar
st.sidebar.title('WM Dashboard')
st.sidebar.subheader('Surveyor')
# multi select box for selecting multiple surveyors
surveyors = st.sidebar.multiselect('Select surveyors', participants_data.getSurveyors())
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
st.markdown('### Participants Report')
# get report data
if len(surveyors) == 0:
    st.markdown('No surveyors selected.')
else:
    reportData = participants_data.generateReport(surveyors, start_date, end_date)
    # display report data
    st.dataframe(reportData)    