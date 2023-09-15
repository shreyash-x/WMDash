import json
from datetime import datetime
import data.fetchMongo as fetchMongo

class MessageData:

    def __init__(self):
        self.data = fetchMongo.getCollectionData('messages')

    def getMessages(self):
        return self.data
    
    def getMessagesFromFile(self, filename):
        if filename is None:
            return None
        return fetchMongo.getGridFSFile(filename)
    
    def getUserNames(self):
        users = []
        for message in self.data:
            name = message['userName'] + ' (' + message['userID'][-4:] + ')'
            if name not in users:
                users.append(name)
        return users
    
    def getChatNames(self, userName):
        if userName is None:
            return []
        chats = []
        for message in self.data:
            name = message['userName'] + ' (' + message['userID'][-4:] + ')'
            if name == userName:
                cname = message['chatName']
                if cname not in chats:
                    chats.append(cname)
        return chats
    
    def getChatMessages(self, userName, chatName):
        if userName is None or chatName is None:
            return None
        for message in self.data:
            name = message['userName'] + ' (' + message['userID'][-4:] + ')'
            if name == userName and message['chatName'] == chatName:
                return self.getMessagesFromFile(message['messages']['filename'])
        return None
    
    def getMessageCount(self, userName):
        data = []
        if userName is None:
            return None
        for message in self.data:
            name = message['userName'] + ' (' + message['userID'][-4:] + ')'
            if name == userName:
                messageData = self.getMessagesFromFile(message['messages']['filename'])
                msgLen = -1
                if messageData != None:
                    msgLen = len(messageData)
                data.append({
                    'Chat': message['chatName'],
                    'FileName': message['messages']['filename'],
                    'Expected Count': message['messages']['length'],
                    'Actual Count': msgLen,
                    'isValid': msgLen == message['messages']['length'],
                });
        return data
    
    def getMediaFileNames(self, userName):
        if userName is None:
            return []
        files = []
        for message in self.data:
            name = message['userName'] + ' (' + message['userID'][-4:] + ')'
            if name == userName:
                messageData = self.getMessagesFromFile(message['messages']['filename'])
                if messageData != None:
                    for msg in messageData:
                        if msg['hasMedia'] == True:
                            if 'mediaDownloaded' in msg and msg['mediaDownloaded'] == True:
                                files.append({
                                    'Chat': message['chatName'],
                                    'FileName': msg['mediaData']['filename'],
                                })
        return files