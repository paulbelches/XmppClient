import sys
import logging
import getpass
from optparse import OptionParser

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
        
        self.add_event_handler("session_start", self.start)
        self.add_event_handler('message', self.incomingMessage)
        self.add_event_handler("changed_status", self.wait_for_presences)

        if self.connect():
            print("Sign in completed")
            self.process(block=False)
        else:
            raise Exception("Unable to connect to Redes Jabber server")

    def start(self, event):
        self.send_presence()
        roster = self.get_roster()
    
    def finish(self):
        self.disconnect(wait=False)

    def register(self):
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
            raise Exception("Unable to connect to Redes Jabber server")
        self.disconnect()
            
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

    def sendMessage(self, recipient, msg):
        print("Sending message")
        self.send_message(mto=recipient,  mbody=msg, mtype='chat')
    
    def sendGroupMessage(self, recipient, msg):
        print("Sending message")
        self.send_message(mto=recipient,  mbody=msg, mtype='groupchat')
        
    def incomingMessage(self, message):
        print(message['from'], message['body'])
    
    def sendPresence(self, presence, status):
        self.send_presence(pshow="dnd", pstatus="Wooing Juliet")
    
    #Change
    def wait_for_presences(self, pres):
        self.received.add(pres['from'].bare)
        if len(self.received) >= len(self.client_roster.keys()):
            self.presences_received.set()
        else:
            self.presences_received.clear()
    
    def contacts(self):
        groups = self.client_roster.groups()
        print("Lista de contactos: ")
        for group in groups:
            for jid in groups[group]:
                print(jid)
                print(self.client_roster[jid]['subscription'])
                print(self.client_roster[jid]['name'])
                print(self.client_roster.presence(jid))

    
   
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
            client.register()
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
        print("|9.  Enviar notificaciones                       |")
        print("|10. Recibir notificaciones                      |")
        print("|11. Enviar archivos                             |")
        print("|12. Recibir archivos                            |")
        print("|13. Remover cuenta                              |")
        print("|------------------------------------------------|")
        print("Ingrese la opción que desea realizar: ")
        op = input()
        if (op == "1"):
            client.contacts()
        if (op == "6"):
            to = "paulbelches@redes2020.xyz"
            message="Holas"
            client.sendMessage(to, message)
        
        if (op == "8"):
            to = "paulbelches@redes2020.xyz"
            message="Holas"
            client.sendPresence(to, message)

        elif (op == "13"):
            client.unregister()
            print("done")
            flag= False
    