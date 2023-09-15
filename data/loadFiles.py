import json
import data.fetchMongo as fetchMongo

class FilesData:

    def __init__(self):
        self.messageFiles = fetchMongo.getGridFSFileNames('message_logs.json')
        self.chatFiles = fetchMongo.getGridFSFileNames('chat_logs.json')
        self.contactFiles = fetchMongo.getGridFSFileNames('contact_logs.json')
        self.mediaFiles = fetchMongo.getGridFSMediaFileNames()

    def getMessageFiles(self):
        return self.messageFiles
    
    def getChatFiles(self):
        return self.chatFiles
    
    def getContactFiles(self):
        return self.contactFiles
    
    def getMediaFiles(self):
        return self.mediaFiles