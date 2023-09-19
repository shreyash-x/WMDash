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

# Sidebar
st.sidebar.title('WM Dashboard')
st.sidebar.subheader('User Name')
userNames = messageData.getUserNames()
userName = st.sidebar.selectbox('Participant', userNames)

st.sidebar.markdown('''
---
Data Visualizer for WhatsappExplorer.
''')

# Page
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
st.markdown('### Unsaved Media Files')
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
message_files_df = pd.DataFrame(messageFiles)
media_files_df = pd.DataFrame(mediaFiles)
chat_files_df = pd.DataFrame(chatFiles)
contact_files_df = pd.DataFrame(contactFiles)
# add a column to identify the type of file
message_files_df['FileType'] = 'Message'
media_files_df['FileType'] = 'Media'
chat_files_df['FileType'] = 'Chat'
contact_files_df['FileType'] = 'Contact'
# combine both dataframes
files_df = pd.concat([message_files_df, media_files_df, chat_files_df, contact_files_df])
files_df['FileSize'] = files_df['FileSize'] / (1024*1024)
files_df = files_df.round(2)
# create a pie chart
fig = px.pie(files_df, values='FileSize', names='FileType', title='Space used by each type of file in MBs')
st.plotly_chart(fig, use_container_width=True)