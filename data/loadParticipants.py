import json
from datetime import datetime
import data.fetchMongo as fetchMongo

class ParticipantsData:

    def __init__(self):
        self.data = fetchMongo.getCollectionData('participants')
        self.reportData = []

    def getSurveyors(self):
        surveyors = fetchMongo.getCollectionData('surveyors')
        data = []
        for surveyor in surveyors:
            data.append(surveyor['username'])
        return data
    
    def getActiveParticipants(self):
        data = []
        for participant in self.data:
            data.append({
                "Count": participant['name'] + ' (' + participant['clientId'][-4:] + ')',
                "Status": "Revoked" if participant['isRevoked'] else "Active"
            })
        return data

    def getClientStatus(self):
        data = []
        for participant in self.data:
            data.append({
                "Name": participant['name'] + ' (' + participant['clientId'][-4:] + ')',
                "Status": participant['clientStatus']
            })
        return data

    def getParticipants(self, minDate, maxDate):
        # get participants with dateOfRegistration between minDate and maxDate
        data = []
        for participant in self.data:
            date = participant['dateOfRegistration'].date()
            if date >= minDate and date <= maxDate:
                data.append(participant)
        return data
    
    def getParticipantsBySurveyors(self, surveyors):
        data = []
        for participant in self.data:
            if participant['addedByName'] in surveyors:
                data.append(participant['name'] + ' (' + participant['clientId'][-4:] + ')')
        return data
    
    def getDOJS(self, participantNames):
        data = {}
        for participant in self.data:
            if participant['name'] + ' (' + participant['clientId'][-4:] + ')' in participantNames:
                data[participant['name'] + ' (' + participant['clientId'][-4:] + ')'] = participant['dateOfRegistration']
        return data

    
    def processConsentedChatUsers(self, participant):
        consentedUsers = set()
        for item in participant['consentedChatUsers']:
            if item[1] == True:
                consentedUsers.add(item[0])
        return consentedUsers
    
    def getChatUserLogs(self, participant):
        clientId = participant['clientId']
        chatUserData = fetchMongo.getCollectionData('chatusers')
        for chatUser in chatUserData:
            if chatUser['userID'] == clientId:
                return fetchMongo.getGridFSFile(chatUser['chats']['filename'])
        return None
    
    def getMessageCount(self, participant):
        count = 0
        messageData = fetchMongo.getCollectionData('messages')
        for message in messageData:
            if message['participantID'] == participant['_id']:
                count += message['messages']['length']
        return count
    
    def processChatUserLogs(self, participant):
        chatLogs = self.getChatUserLogs(participant)
        consentedUsers = self.processConsentedChatUsers(participant)
        data = {
            'name': participant['name'] + ' (' + participant['clientId'][-4:] + ')',
            'DOJ': participant['dateOfRegistration'],
            'Status': "Revoked" if participant['isRevoked'] else "Available",
            'surveyor': participant['addedByName'],
            'totalIndividualChats': 0,
            'totalGroups': 0,
            'eligibleGroups': 0,
            'defaultSelectedGroups': 0,
            'deselectedGroups': 0,
            'additionalSelectedGroups': 0,
            'consentedGroups': 0,
            'messagesLogged': 0,
            # 'surveyResults': participant['surveyResults'],
        }
        if chatLogs is not None:
            for chat in chatLogs:
                if chat['isGroup']:
                    data['totalGroups'] += 1
                    if 'num_participants' not in chat:
                        chat['num_participants'] = len(chat['groupMetadata']['participants'])
                    if chat['num_participants'] >= 5:
                        data['eligibleGroups'] += 1
                        if 'num_messages' in chat and chat['num_messages'] >= 15:
                            data['defaultSelectedGroups'] += 1
                            if chat['id']['_serialized'] not  in consentedUsers:
                                data['deselectedGroups'] += 1
                    if chat['id']['_serialized'] in consentedUsers:
                        data['consentedGroups'] += 1
                else:
                    data['totalIndividualChats'] += 1

        data['additionalSelectedGroups'] = data['consentedGroups'] - data['defaultSelectedGroups'] + data['deselectedGroups']
        data['messagesLogged'] = self.getMessageCount(participant)
        return data
    
    def generateReport(self, surveyors, minDate, maxDate):
        participants = self.getParticipants(minDate, maxDate)
        for participant in participants:
            if participant['addedByName'] in surveyors:
                self.reportData.append(self.processChatUserLogs(participant))
        return self.reportData
    

                