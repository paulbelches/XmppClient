import sys
import logging
import getpass
import sleekxmpp
from sleekxmpp.exceptions import IqError, IqTimeout
from sleekxmpp.xmlstream.stanzabase import ET, ElementBase

class Client(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)
        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0004') # Data forms
        self.register_plugin('xep_0066') # Out-of-band Data
        self.register_plugin('xep_0077') # In-band Registration
        self.register_plugin('xep_0199') # XMPP Ping
        
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
        self.send_message(mto=recipient,  mbody=msg, mtype='chat')
    
    #When the event is trigger prints the recieve message
    def incomingMessage(self, message):
        print(message['from'], message['body'])
    
    """
   o  away -- The entity or resource is temporarily away.

   o  chat -- The entity or resource is actively interested in chatting.

   o  dnd -- The entity or resource is busy (dnd = "Do Not Disturb").

   o  xa -- The entity or resource is away for an extended period (xa =
      "eXtended Away").
    """

    #Change precense
    def sendPresence(self, presence, status):
        self.send_presence(pshow="dnd", pstatus="Wooing Juliet")
    
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
    
    def sendGroupMessage(self, recipient, msg):
        print("Sending message")
        self.send_message(mto=recipient,  mbody=msg, mtype='groupchat')

    def joinRoom(self, roomName, name):   
        try:
            self.plugin['xep_0045'].joinMUC(roomName, name, wait=True)
        except IqError as e:
            pass
            #raise Exception("Unable to create room", e)
        except IqTimeout:
            pass
            #raise Exception("Server not responding")  

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
            #user = input("Ingrese su JID: ")
            #password =  getpass.getpass(prompt='Ingrese su contraseña: ')  
            #user = "paulbelches@redes2020.xyz"
            #password = "password"
            user = "bel17088@redes2020.xyz"
            password = "jesus"
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
        print("|1.  Mostrar todos los usuarios                  |")
        print("|3.  Mostrar contactos y su estado               |")
        print("|4.  Agregar un usuario a los contactos          |")
        print("|5.  Mostrar detalles de contacto de un usuario  |")
        print("|6.  Mensaje Directo                             |")
        print("|7.  Mandar un mensaje a un grupo                |")
        print("|8.  Definir mensaje de presencia                |")
        print("|9.  Mandar notificacion                         |")
        print("|11. Enviar archivos                             |")
        print("|13. Remover cuenta                              |")
        print("|------------------------------------------------|")
        print("Ingrese la opción que desea realizar: ")
        op = input()
        if (op == "1"):
            client.getUsers()
        if (op == "3"):
            client.contacts()
        if (op == "4"):
            username = "davidsoto@redes2020.xyz"
            client. addUser(username)
        if (op == "5"):
            username = "holo"
            client.getUsersInfo(username)
        if (op == "6"):
            to = "tru@redes2020.xyz"
            message="Holas"
            client.sendMessage(to, message)
        if (op == "8"):
            to = "paulbelches@redes2020.xyz"
            message="Holas"
            client.sendPresence(to, message)
        if (op == "9"):
            message="Toy por aca"
            client.sendNotification(message)
        if (op == "10"):
            client.finish()
        elif (op == "13"):
            #Eliminate account
            client.unregister()
            print("done")
            flag= False
    