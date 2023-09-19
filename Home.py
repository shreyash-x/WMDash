import streamlit as st
import pandas as pd
import plost
import plotly.express as px
import datetime


st.set_page_config(layout='wide', initial_sidebar_state='expanded', page_title='WMDash', page_icon=':bar_chart:')
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.markdown('''
# WhatsappExplorer Dashboard

This dashboard is a data visualizer for WhatsappExplorer built using Streamlit specifically for
monitoring the WhatsappExplorer tool.  
**The dashboard contain 3 pages:**
- **Messages:** This page shows messages collected for each participant in a specific chat.
- **Files:** This page shows the files in which the data collected is stored in the database (GridFS).
- **Participants:** This page shows the report of the participants added to the tool.
''')
            
