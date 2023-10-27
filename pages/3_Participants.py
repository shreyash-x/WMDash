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
options = participants_data.getSurveyors()
surveyors = st.sidebar.multiselect('Select surveyors', options)
all_options = st.sidebar.checkbox("Select all options")
if all_options:
    surveyors = options
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
    st.download_button(
    "Download",
    pd.DataFrame(reportData).to_csv(index=False).encode('utf-8'),
    "report.csv",
    "text/csv",
    key='download-csv'
    )    
    
st.markdown('### Participants Status')
participantStatus = participants_data.getActiveParticipants()
pdf = pd.DataFrame(participantStatus).groupby(by=['Status'], as_index=False).count()
fig = px.pie(pdf, values='Count', names='Status', title='Status of clients in the WhatsappExplorer')
st.plotly_chart(fig, use_container_width=True)