import sys
import logging
import getpass
import base64
import sleekxmpp
from sleekxmpp.exceptions import IqError, IqTimeout
from sleekxmpp.xmlstream.stanzabase import ET, ElementBase

#===============================#
#Paul Belches                   #
#paulbelches@gmail.com          #
#===============================#
#Xmpp client implmentation v1.0 #
# 24/09/20                      #
#===============================#

class Client(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password):

        self.fileCounter = 0

        sleekxmpp.ClientXMPP.__init__(self, jid, password)
        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0004') # Data forms
        self.register_plugin('xep_0066') # Out-of-band Data
        self.register_plugin('xep_0077') # In-band Registration
        self.register_plugin('xep_0199') # XMPP Ping
        self.register_plugin('xep_0045') # Room managment
        
        #Event hadlers trigger functions when a event happens
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("got_online", self.onlineNotifications)
        self.add_event_handler("got_offline", self.offlineNotifications)
        self.add_event_handler("changed_status", self.changedStatusNotifications)
        self.add_event_handler('message', self.incomingMessage)

        if self.connect():
            print("Sign in completed")
            self.process(block=False)
        else:
            print("Could not connect")

    #Handler for users going online
    #When the event is trigger prints the new online user
    #@Event event that trigger the handdler
    def onlineNotifications(self, event):
        if (event['from'].user != self.jid.split("@")[0]):
            print(event['from'].user, " just login")

    #Handler for users going offline
    #When the event is trigger prints the new offline user
    #@Event event that trigger the handdler
    def offlineNotifications(self, event):
        if (event['from'].user != self.jid.split("@")[0]):
            print(event['from'].jid, " just logout")
    
    #Handler for users changing presence
    #When the event is trigger prints that a user has chence its presence
    #@Event event that trigger the handdler
    def changedStatusNotifications(self, event):
        if (event['from'].user != self.jid.split("@")[0]):
            print(event['from'].jid, " just change status")

    #Login function
    #@Event event that trigger the handdler
    def start(self, event):
        self.send_presence(pshow="chat", pstatus="Ready to start") #Establish intial presence 
    
    #Logout function
    def finish(self):
        self.disconnect(wait=False) #Disconnect clinet

    #Register client in server
    def register(self):
        resp = self.Iq() #Create iq Stanza
        #Stanza config
        resp['type'] = 'set'
        resp['register']['username'] = self.jid.split("@")[0]
        resp['register']['password'] = self.password
        try:
            resp.send(now=True) #Send Stanza
            print("Creating account")
        #Error Handling
        except IqError as e:
            print(e)
            print("Could not register account ")
            self.disconnect()
        #Time out handling Handling
        except IqTimeout:
            pprint("Server did no respond")
            self.disconnect()

        #Check if conection was established
        if self.connect():
            self.process(block=False)
        else:
            pass
            #error print
        self.disconnect()

    #Eliminate account from server        
    def unregister(self):#Create iq Stanza
        resp = self.Iq()
        resp['type'] = 'set'
        resp['from'] = self.jid 
        resp['id'] = 'unreg1'
        query = "<query xmlns='jabber:iq:register'>\
                <remove/>'\
                </query> "
        resp.append(ET.fromstring(query))
        try:
            print("Removing account.....")
            resp.send(now=True)
        #Error Handling
        except IqError as e:
            print("Could not remove account")
            self.disconnect()
        #Time out handling Handling
        except IqTimeout:
            print("Server did no respond")
            self.disconnect()

    #Send direct message
    #@recipient User that is going to recive the message
    #@msg Message that is going to be send
    def sendMessage(self, recipient, msg):
        print("Sending message")
        try:
            self.send_message(mto=recipient,  mbody=msg, mtype="chat")
        except IqError as e:
            print("Could not send message")
        except IqTimeout:
            print("Server did no respond")

    #Change precense
    #@show Show that is going to be show
    #@status Status that is going to be show
    def sendPresence(self, show, status):
        self.send_presence(pshow=show, pstatus=status)
    
    #Add user to roster
    #@jid JID From the user we are going to add to rooster
    def addUser(self, jid):
        self.send_presence_subscription(pto=jid)
    
    #List all roster users
    def contacts(self):
        groups = self.client_roster.groups() #get all roster gropus
        print("Contact list: ")
        for group in groups:
            for jid in groups[group]: #get all roster Jids in group
                print('-------------------------------------------')
                #Print JID
                print("JID: ", jid)
                if (len(self.client_roster[jid]['name']) > 0):
                    print("Name: ",self.client_roster[jid]['name'])
                else: 
                    print("--- There is no name register ---")
                #Print JID
                presences = self.client_roster.presence(jid)
                if (len(self.client_roster.presence(jid)) < 1):
                    print("--- There is no presence register ---")
                else:
                    for p in presences:
                        print('     Resource: ', p)
                        print('     Show: ', presences[p]['show'])
                        print('     Status: ', presences[p]['status'])
                print('-------------------------------------------')
    
    #List all existing users in server
    def getUsers(self):
        #Create iq Stanza
        resp = self.Iq()
        resp['type'] = 'set'
        resp['to'] = 'search.redes2020.xyz'
        resp['from'] =  self.jid 
        resp['id'] = 'search_result'
        #Service discovery stanza for getting all users
        resp.append(ET.fromstring("<query xmlns='jabber:iq:search'>\
                                 <x xmlns='jabber:x:data' type='submit'>\
                                    <field type='hidden' var='FORM_TYPE'>\
                                        <value>jabber:iq:search</value>\
                                    </field>\
                                    <field var='Username'>\
                                        <value>1</value>\
                                    </field>\
                                    <field var='search'>\
                                        <value>*</value>\
                                    </field>\
                                </x>\
                            </query>"))
        try:
            results = resp.send()
            # Extract info from recived stanza
            for i in results.findall('.//{jabber:x:data}value'): 
                if ((i.text != None) and ("@" in i.text)):
                    print(i.text)
        except IqError as e:
            print("Could not get users")
        except IqTimeout:
            print("Server did no respond")
    
    #Send notification
    #@body Notification body
    def sendNotification(self,  body):
        #Create meesage Stanza
        message = self.Message()
        message['type'] = 'chat'
        message['body'] = body
        message.append(ET.fromstring("<active xmlns='http://jabber.org/protocol/chatstates'/>"))
        #Get all elements in roster
        groups = self.client_roster.groups()
        for group in groups:
            for jid in groups[group]:
                message['to'] = jid #JID
                try:
                    message.send()
                except IqError as e:
                    print("Could not send notification")
                except IqTimeout:
                    print("Server did no respond")

    #Get info from user
    #@JID from the user
    def getUsersInfo(self, jid):
        #Create iq Stanza
        resp = self.Iq()
        resp['type'] = 'set'
        resp['to'] = 'search.redes2020.xyz'
        resp['from'] =  self.jid 
        resp['id'] = 'search_result'
        #Service discovery stanza for getting a user
        resp.append(ET.fromstring(
            "<query xmlns='jabber:iq:search'>\
                <x xmlns='jabber:x:data' type='submit'>\
                    <field type='hidden' var='FORM_TYPE'>\
                        <value>jabber:iq:search</value>\
                    </field>\
                    <field var='Username'>\
                        <value>1</value>\
                    </field>\
                    <field var='search'>\
                        <value>"+jid+"</value>\
                    </field>\
                </x>\
            </query>"))
        try:
            results = resp.send()
            # Extract info from recived stanza
            for i in results.findall('.//{jabber:x:data}value'):
                if (i.text != None):
                    print(i.text)
        except IqError as e:
            pass
        except IqTimeout:
            pass

    #Join a room
    #@roomName the name of the room we are going to join
    #@name The nickname we are going to have in the group
    def joinRoom(self, roomName, name):   
        try:
            room = roomName + "@conference.redes2020.xyz"
            self.plugin['xep_0045'].joinMUC(room, name, wait=True)
        except IqError as e:
            print("Could not join room")
        except IqTimeout:
            pass
            print("Server did no respond")


    #Create a room
    #@roomName the name of the room we are going to create
    #@name The nickname we are going to have in the group
    def createRoom(self, roomName, name):   
        try:
            room = roomName + "@conference.redes2020.xyz"
            self.plugin['xep_0045'].joinMUC(room, name, wait=True)
            roomform = self.plugin['xep_0045'].getRoomConfig(room)
            roomform.set_values({
                'muc#roomconfig_persistentroom': 1,
            })
            self.plugin['xep_0045'].configureRoom(room, form=roomform)
        except IqError as e:
            print("Could not create room")
        except IqTimeout:
            print("Server did no respond") 

    #Handler for incoming messages
    #When the event is trigger prints the recieve message
    #@Event event that trigger the handdler
    def incomingMessage(self, message):
        #Check if it has the reciving file Flag
        if(message['body'][:4] == "FILE"):
            print("Entre")
            print("File receive from " , message['from'])
            print("File saved in ", str(self.fileCounter))
            extension = message['body'][4:14].replace(" ", "")
            fileBinarys = message['body'][14:]
            ff = open(str(self.fileCounter)+"."+extension, "xb")
            ff.write(base64.decodebytes(fileBinarys.encode('utf-8')))
            ff.close()
        #If not print the received message
        else:
            print(message['from'], message['body'])
    
    #Makes a 10 character long string
    #@extension Original string
    def complete(self,extension):
        while (len(extension)<10):            
            extension = extension + " "
        return extension

    #Send group messge
    #@recipient Group that is going to recive the message
    #@msg Message that is going to be send
    def sendGroupMessage(self, recipient, msg):
        print("Sending message")
        self.send_message(mto=recipient,  mbody=msg, mtype='groupchat')

    #Send File
    def sendFile(self, recipient, filename, filext):
        try: 
            of = open(filename+"."+filext, "rb")
            lines = base64.b64encode(of.read()).decode('utf-8')
            extension = self.complete(filext)  
            #Add flag FILE
            #Next 10 chacters is the extension
            #Then comes the file
            message = "FILE"+extension+lines
            try:
                self.send_message(mto=recipient,  mbody=message, mtype="chat")
            except IqError as e:
                print("Could not send file")
            except IqTimeout:
                print("Server did no respond")
        except:
            print("Error loading file")
   

#====================================================================================0
import getpass 
user = ""
password = ""
client = None
flag = True 
while(flag):
    if (len(user)+len(password) == 0):
        print("|----------------------Menu----------------------|")
        print("|1.  Log in                                      |")
        print("|2.  Sign up                                     |")
        print("|------------------------------------------------|")
        print("Enter the number of the option: ")
        op = input()
        if (op == "1"):
            user = input("Enter username: ")
            password =  getpass.getpass(prompt='Enter password: ')  
            user = user + "@redes2020.xyz"
            client = Client(user, password)
        elif (op == "2"):
            user = input("Enter username: ")
            password =  getpass.getpass(prompt='Enter password: ')  
            user = user + "@redes2020.xyz"
            client = Client(user, password) 
            client.register()
            client = Client(user, password) 
    else:
        print("|----------------------Menu----------------------|")
        print("|1.  Show all registered users                   |")
        print("|2.  Show all contacts with their state          |")
        print("|3.  Add user to roster                          |")
        print("|4.  Show user info                              |")
        print("|5.  Direct message                              |")
        print("|6.  Group message                               |") #Add group validation
        print("|7.  Define presence                             |")
        print("|8.  Send notification                           |")
        print("|9.  Join group                                  |")
        print("|10. Send File                                   |")
        print("|11. Create group                                |")
        print("|12. Delete account                              |")
        print("|13. Log off                                     |")
        print("|------------------------------------------------|")
        print("Enter the number of the option: ")
        op = input()
        if (op == "1"): #Show all users
            client.getUsers()
        if (op == "2"): #Show all contacts 
            client.contacts()
        if (op == "3"): #Add user to roster
            username  = input("Enter the username: ")
            client.addUser(username + "@redes2020.xyz")
        if (op == "4"): #Show user info
            username = input("Enter the username: ")
            client.getUsersInfo(username)
        if (op == "5"): #Send direct message
            to = input("Enter the username: ")
            message= input("Enter the message: ")
            client.sendMessage(to+"@redes2020.xyz", message)
        if (op == "6"): #Send group message
            to = input("Enter the groupname: ")
            message= input("Enter the message: ")
            client.sendGroupMessage(to+"@conference.redes2020.xyz", message)
        if (op == "7"): #Define presence
            show = input("Enter what you wish to show (Ex. away, chat, dnd, xa): ")
            presence = input("Enter your new presence: ")
            client.sendPresence(show, presence)
        if (op == "8"): #Send Notification
            notification  = input("Enter the notification: ")
            client.sendNotification(notification)
        if (op == "9"): #Join room
            roomName = input("Enter the groupname: ")
            client.joinRoom(roomName, user.split('@')[0])
        if (op == "10"): #Send file|Add validation
            to = input("Enter the username: ")
            filename = input("Enter file path (ex. gundam.jpeg, requirements.txt): ")
            fileProps = filename.split(".")
            client.sendFile(to+"@redes2020.xyz",fileProps[0],fileProps[1])
        if (op == "11"): #Create room
            roomName = input("Enter the groupname: ")
            client.createRoom(roomName, user.split('@')[0])
        if (op == "12"):#Unregister account
            #Eliminate account
            flag= False
            client.unregister()
            print("done")
        if (op == "13"):#Log off
            client.finish()
            flag= False
    