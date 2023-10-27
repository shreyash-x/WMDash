import json
from datetime import datetime
import data.fetchMongo as fetchMongo

class ChatuserData:

    def __init__(self):
        self.data = fetchMongo.getCollectionData('chatusers')
        self.participants = fetchMongo.getCollectionData('participants')
    
    def getChatusersFromFile(self, filename):
        if filename is None:
            return None
        return fetchMongo.getGridFSFile(filename)
    
    def getUserNames(self):
        users = []
        for user in self.participants:
            name = user['name'] + ' (' + user['clientId'][-4:] + ')'
            if name not in users:
                users.append(name)
        return users
    
    def getChatusers(self, userName):
        if userName is None:
            return None
        for chatuser in self.data:
            name = chatuser['userName'] + ' (' + chatuser['userID'][-4:] + ')'
            if name == userName:
                return self.getChatusersFromFile(chatuser['chats']['filename'])
        return None