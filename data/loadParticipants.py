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


    def getParticipants(self, minDate, maxDate):
        # get participants with dateOfRegistration between minDate and maxDate
        data = []
        for participant in self.data:
            date = participant['dateOfRegistration'].date()
            if date >= minDate and date <= maxDate:
                data.append(participant)
        return data
    
    def processConsentedChatUsers(self, participant):
        consentedUsers = {}
        for item in participant['consentedChatUsers']:
            consentedUsers[item[0]] = item[1]
        return consentedUsers
    
    def getChatUserLogs(self, participant):
        clientId = participant['clientId']
        chatUserData = fetchMongo.getCollectionData('chatUsers')
        for chatUser in chatUserData:
            if chatUser['userID'] == clientId:
                return fetchMongo.getGridFSFile(chatUser['chats']['filename'])
        return None
    
    def getMessageCount(self, participant):
        count = 0
        messageData = fetchMongo.getCollectionData('messages')
        for message in messageData:
            if message['participantID'] == participant['_id']:
                count += 1
        return count
    
    def processChatUserLogs(self, participant):
        chatLogs = self.getChatUserLogs(participant)
        consentedUsers = self.processConsentedChatUsers(participant)
        data = {
            'name': participant['name'],
            'DOJ': participant['dateOfRegistration'],
            'surveyor': participant['addedByName'],
            'eligibleGroups': 0,
            'consentedGroups': 0,
            'totalGroups': 0,
            'totalIndividualChats': 0,
            'defaultSelectedGroups': 0,
            'deselectedGroups': 0,
            'additionalSelectedGroups': 0,
            'messagesLogged': 0,
            # 'surveyResults': participant['surveyResults'],
        }
        if chatLogs is not None:
            for chat in chatLogs:
                if chat['isGroup']:
                    data['totalGroups'] += 1
                    if chat['num_participants'] >= 5:
                        data['eligibleGroups'] += 1
                        if chat['num_messages'] >= 15:
                            data['defaultSelectedGroups'] += 1
                            if not consentedUsers[chat['id']['_serialized']]:
                                data['deselectedGroups'] += 1
                    if consentedUsers[chat['id']['_serialized']]:
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
    

                