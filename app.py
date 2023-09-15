import streamlit as st
import pandas as pd
import plost
import plotly.express as px
import datetime
# Data Loading
import data.loadMessages as loadMessages
import data.loadFiles as loadFiles

messageData = loadMessages.MessageData()
filesData = loadFiles.FilesData()

st.set_page_config(layout='wide', initial_sidebar_state='expanded')
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Tabs
Messages, Files = st.tabs(['Messages', 'Files'])


    
st.sidebar.title('WM Dashboard')

# Sidebar Parameters
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
                    


with Messages:
    # Row A
    st.markdown('### Selected User Message Stats')
    messages = messageData.getMessageCount(userName)
    if messages is None or len(messages) == 0:
        st.markdown('Please select a user from the sidebar.')
    else:
        st.dataframe(messages)


    # Row A
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


with Files:

    # Show filename and filesize of all message files
    st.markdown('### Message Files')
    messageFiles = filesData.getMessageFiles()
    if messageFiles is None or len(messageFiles) == 0:
        st.markdown('No message files found.')
    else:
        message_files_df = pd.DataFrame(messageFiles)
        if userName is not None:
            messages = messageData.getMessageCount(userName)
            message_df = pd.DataFrame(messages)
            # join message files with message data based on FileName
            message_files_df = message_files_df.merge(message_df, left_on='FileName', right_on='FileName')
            message_files_df = message_files_df[['Chat', 'FileName', 'FileSize', 'Expected Count', 'Actual Count', 'isValid']]
            # convert filesize to MB
            message_files_df['FileSize'] = message_files_df['FileSize'] / (1024*1024)
        st.dataframe(
            message_files_df.style.format({
                'FileSize': '{:.2f} MB',
            })
        )

    # Show filename and filesize of all media files
    st.markdown('### Media Files')
    mediaFiles = filesData.getMediaFiles()
    if mediaFiles is None or len(mediaFiles) == 0:
        st.markdown('No media files found.')
    else:
        media_files_df = pd.DataFrame(mediaFiles)
        if userName is not None:
            mediaData = messageData.getMediaFileNames(userName)
            message_media_df = pd.DataFrame(mediaData)
            # join message files with message data based on FileName
            media_files_df = media_files_df.merge(message_media_df, left_on='FileName', right_on='FileName')
            media_files_df = media_files_df[['Chat', 'FileName', 'FileSize']]
            # convert filesize to MB
            media_files_df['FileSize'] = media_files_df['FileSize'] / (1024*1024)
        st.dataframe(
            media_files_df.style.format({
                'FileSize': '{:.2f} MB',
            })
        )


    # Create a pie chart of the space used by each type of file using plotly
    st.markdown('### Space used')
    chatFiles = filesData.getChatFiles()
    contactFiles = filesData.getContactFiles()
    if messageFiles is None or len(messageFiles) == 0:
        st.markdown('No message files found.')
    elif mediaFiles is None or len(mediaFiles) == 0:
        st.markdown('No media files found.')
    elif chatFiles is None or len(chatFiles) == 0:
        st.markdown('No chat files found.')
    elif contactFiles is None or len(contactFiles) == 0:
        st.markdown('No contact files found.')
    else:
        message_files_df = pd.DataFrame(messageFiles)
        media_files_df = pd.DataFrame(mediaFiles)
        chat_files_df = pd.DataFrame(chatFiles)
        contact_files_df = pd.DataFrame(contactFiles)
        # convert filesize to MB
        message_files_df['FileSize'] = message_files_df['FileSize'] / (1024*1024)
        media_files_df['FileSize'] = media_files_df['FileSize'] / (1024*1024)
        chat_files_df['FileSize'] = chat_files_df['FileSize'] / (1024*1024)
        contact_files_df['FileSize'] = contact_files_df['FileSize'] / (1024*1024)
        # add a column to identify the type of file
        message_files_df['FileType'] = 'Message'
        media_files_df['FileType'] = 'Media'
        chat_files_df['FileType'] = 'Chat'
        contact_files_df['FileType'] = 'Contact'
        # combine both dataframes
        files_df = pd.concat([message_files_df, media_files_df, chat_files_df, contact_files_df])
        # create a pie chart
        fig = px.pie(files_df, values='FileSize', names='FileType', title='Space used by each type of file')
        st.plotly_chart(fig, use_container_width=True)

    



# Row B
# seattle_weather = pd.read_csv('https://raw.githubusercontent.com/tvst/plost/master/data/seattle-weather.csv', parse_dates=['date'])
# stocks = pd.read_csv('https://raw.githubusercontent.com/dataprofessor/data/master/stocks_toy.csv')

# c1, c2 = st.columns((7,3))
# with c1:
#     st.markdown('### Heatmap')
#     plost.time_hist(
#     data=seattle_weather,
#     date='date',
#     x_unit='week',
#     y_unit='day',
#     color=time_hist_color,
#     aggregate='median',
#     legend=None,
#     height=345,
#     use_container_width=True)
# with c2:
#     st.markdown('### Donut chart')
#     plost.donut_chart(
#         data=stocks,
#         theta=donut_theta,
#         color='company',
#         legend='bottom', 
#         use_container_width=True)

# # Row C
# st.markdown('### Line chart')
# st.line_chart(seattle_weather, x = 'date', y = plot_data, height = plot_height)
