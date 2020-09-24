import sys
import logging
import getpass
import base64
import sleekxmpp
from sleekxmpp.exceptions import IqError, IqTimeout
from sleekxmpp.xmlstream.stanzabase import ET, ElementBase

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
            raise Exception("Unable to connect to Redes Jabber server")

    #When the event is trigger prints the new online user
    def onlineNotifications(self, event):
        if (event['from'].user != self.jid.split("@")[0]):
            print(event['from'].user, " just login")
    
    #When the event is trigger prints the new offline user
    def offlineNotifications(self, event):
        if (event['from'].user != self.jid.split("@")[0]):
            print(event['from'].jid, " just logout")
    
    #When the event is trigger prints that a user has chence its presence
    def changedStatusNotifications(self, event):
        if (event['from'].user != self.jid.split("@")[0]):
            print(event['from'].jid, " just change status")

    #Login
    def start(self, event):
        self.send_presence(pshow="chat", pstatus="Ready to start")
        self.get_roster()
    
    #Logout
    def finish(self):
        self.disconnect(wait=False)

    #Singup
    def register(self, username):
        resp = self.Iq()
        resp['type'] = 'set'
        resp['register']['username'] = "bel17088"
        resp['register']['password'] = self.password

        try:
            resp.send(now=True)
            print("Creating account")
        except IqError as e:
            print(e)
            print("Could not register account ")
            self.disconnect()
        except IqTimeout:
            print("No response from server.")
            self.disconnect()

        if self.connect():
            print("Account created")
            self.process(block=False)
        else:
            pass
            #error print
        self.disconnect()

    #Eliminate account from server        
    def unregister(self):
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
        except IqError as e:
            print("Could not remove account")
            self.disconnect()
        except IqTimeout:
            print("No response from server.")
            self.disconnect()

    #Send direct message
    def sendMessage(self, recipient, msg):
        print("Sending message")
        try:
            self.send_message(mto=recipient,  mbody=msg, mtype="chat")
        except IqError as e:
            print("Unable to send image")
        except IqTimeout:
            print("Server not responding")

    #Change precense
    def sendPresence(self, show, status):
        self.send_presence(pshow=show, pstatus=status)
    
    #Add user to roster
    def addUser(self, jid):
        self.send_presence_subscription(pto=jid)
    
    #List all roster users
    def contacts(self):
        groups = self.client_roster.groups()
        print("Contact list: ")
        for group in groups:
            for jid in groups[group]:
                print('-------------------------------------------')
                print("JID: ", jid)
                if (len(self.client_roster[jid]['name']) > 0):
                    print("Name: ",self.client_roster[jid]['name'])
                else: 
                    print("--- There is no name register ---")
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
        resp = self.Iq()
        resp['type'] = 'set'
        resp['to'] = 'search.redes2020.xyz'
        resp['from'] =  self.jid 
        resp['id'] = 'search_result'
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
            for i in results.findall('.//{jabber:x:data}value'):
                if ((i.text != None) and ("@" in i.text)):
                    print(i.text)
        except IqError as e:
            pass
        except IqTimeout:
            pass
    
    #Send notification
    def sendNotification(self,  body):
        message = self.Message()
        message['type'] = 'chat'
        message['body'] = body
        message.append(ET.fromstring("<active xmlns='http://jabber.org/protocol/chatstates'/>"))
    
        groups = self.client_roster.groups()
        for group in groups:
            for jid in groups[group]:
                message['to'] = jid #JID
                try:
                    message.send()
                except IqError as e:
                    print("Could not send notification")
                except IqTimeout:
                    print("Server not responding")

    #Get info from user
    def getUsersInfo(self, jid):
        resp = self.Iq()
        resp['type'] = 'set'
        resp['to'] = 'search.redes2020.xyz'
        resp['from'] =  self.jid 
        resp['id'] = 'search_result'
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
            for i in results.findall('.//{jabber:x:data}value'):
                if (i.text != None):
                    print(i.text)
        except IqError as e:
            pass
        except IqTimeout:
            pass

    def joinRoom(self, roomName, name):   
        try:
            self.plugin['xep_0045'].joinMUC(roomName, name, wait=True)
        except IqError as e:
            print("Unable to join room")
        except IqTimeout:
            pass
            print("Server not responding")  

    def createRoom(self, roomName, name):   
        try:
            self.plugin['xep_0045'].joinMUC(roomName, name, wait=True)
        except IqError as e:
            print("Unable to join room")
        except IqTimeout:
            pass
            print("Server not responding")  

    #When the event is trigger prints the recieve message
    def incomingMessage(self, message):
        if(message['body'][:4] == "FILE"):
            print("Entre")
            print("File receive from " , message['from'])
            print("File saved in ", str(self.fileCounter))
            extension = message['body'][4:14].replace(" ", "")
            fileBinarys = message['body'][14:]
            ff = open(str(self.fileCounter)+"."+extension, "xb")
            ff.write(base64.decodebytes(fileBinarys.encode('utf-8')))
            ff.close()
        else:
            print(message['from'], message['body'])
    
    def complete(self,extension):
        while (len(extension)<10):            
            extension = extension + " "
        return extension

    def sendGroupMessage(self, recipient, msg):
        print("Sending message")
        self.send_message(mto=recipient,  mbody=msg, mtype='groupchat')
    #Send File
    def sendFile(self, recipient, filename, filext):
        try: 
            of = open(filename+"."+filext, "rb")
            lines = base64.b64encode(of.read()).decode('utf-8')
            extension = self.complete(filext)
            message = "FILE"+extension+lines
            try:
                self.send_message(mto=recipient,  mbody=message, mtype="chat")
            except IqError as e:
                print("Unable to send image")
            except IqTimeout:
                print("Server not responding")
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
        print("|1.  Iniciar Sesión                              |")
        print("|2.  Registrarse                                 |")
        print("|------------------------------------------------|")
        print("Ingrese la opción que desea realizar: ")
        op = input()
        if (op == "1"):
            user = input("Ingrese su username: ")
            password =  getpass.getpass(prompt='Ingrese su contraseña: ')  
            #user = "paulbelches@redes2020.xyz"
            #password = "password"
            user = user + "@redes2020.xyz"
            #password = "jesus"
            client = Client(user, password)

        elif (op == "2"):
            #user = input("Ingrese su usuario: ")
            #password =  getpass.getpass(prompt='Ingrese su contraseña: ')
            user = "bel17088@redes2020.xyz"
            password = "jesus"
            client = Client(user, password) 
            client.register(user)
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
        print("|8.  Mandar notificacion                         |")
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
        if (op == "3"): #Add user to roster|Add name and check if it works well
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
        if (op == "8"): #Send Notification|Not yet checked
            username  = input("Enter the message: ")
            message="Toy por aca"
            client.sendNotification(message)
        if (op == "9"): #Join room|Not yet checked
            roomName = input("Enter the groupname: ")
            client.joinRoom(roomName+"@conference.redes2020.xyz", user.split('@')[0])
        if (op == "10"): #Send file |Add validation
            to = input("Enter the username: ")
            filename = input("Enter file path (ex. gundam.jpeg): ")
            fileProps = filename.split(".")
            client.sendFile(to+"@redes2020.xyz",fileProps[0],fileProps[1])
        if (op == "11"):
            to = input("Ingrese su username: ")
            #Work in progress
        if (op == "12"):
            #Eliminate account
            client.unregister()
            print("done")
            flag= False
        if (op == "13"): #Log off
            client.finish()
            flag= False
    