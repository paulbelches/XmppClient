import sys
import logging
import getpass
from optparse import OptionParser

import sleekxmpp
from sleekxmpp.exceptions import IqError, IqTimeout

class Client(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)

    def start(self, event):
        self.send_presence()
        self.get_roster()
        self.disconnect()
        
    def sendMessage(self, recipient, msg):
        self.recipient = recipient
        self.msg = msg
        self.add_event_handler("session_start", self.message, threaded=True)

    def message(self, event):
        self.send_presence()
        self.get_roster()
        self.send_message(mto=self.recipient,
                          mbody=self.msg,
                          mtype='chat')
        self.disconnect(wait=True)
        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0199') # XMPP Ping
    
    def removeUser(self, recipient):
        self.recipient = recipient
        self.add_event_handler("register", self.unregister)

    def unregister(self, iq):
        self.send_presence()
        self.get_roster()
        resp = self.Iq()
        resp['type'] = 'set'
        resp['remove']['username'] = self.recipient
        try:
            resp.send(now=True)
            print("Account Remove for ", self.boundjid)
        except IqError as e:
            print("Could not unregister account")
            self.disconnect()
        except IqTimeout:
            print("No response from server.")
            self.disconnect()

#====================================================================================0
import getpass 

user = ""
password = ""
client = None



while(True):
    if (len(user)+len(password) == 0):
        print("|----------------------Menu----------------------|")
        print("|1.  Iniciar Sesión                              |")
        print("|2.  Registrarse                                 |")
        print("|------------------------------------------------|")
        op = input("Ingrese la opción que desea realizar: ")
        if (op == "1"):
            #user = input("Ingrese su JID: ")
            #password =  getpass.getpass(prompt='Ingrese su contraseña: ')  
            user = "paulbelches@redes2020.xyz"
            password = "password"
            client = Client(user, password)
        elif (op == "2"):
            user = input("Ingrese su usuario: ")
            password =  getpass.getpass(prompt='Ingrese su contraseña: ')
            client = Client(user, password) 
                
    else:
        print("|----------------------Menu----------------------|")
        print("|1.  Mostrar todos los usuarios                  |")
        print("|3.  Mostrar contactos y su estado               |")
        print("|4.  Agregar un usuario a los contactos          |")
        print("|5.  Mostrar detalles de contacto de un usuario  |")
        print("|6.  Mensaje Directo                             |")
        print("|7.  Participar en conversaciones grupales       |")
        print("|8.  Definir mensaje de presencia                |")
        print("|9.  Enviar notificaciones                       |")
        print("|10. Recibir notificaciones                      |")
        print("|11. Enviar archivos                             |")
        print("|12. Recibir archivos                            |")
        print("|13. Remover cuenta                              |")
        print("|------------------------------------------------|")
        op = input("Ingrese la opción que desea realizar: ")
        if (op == "6"):
            to = "theroom@redes2020.xyz"
            message="Holas"
            client.sendMessage(to, message)
            if client.connect():
                client.process(block=True)
                print("Done")
            else:
                print("Unable to connect.")
        if (op == "13"):
            to = "bel17088@redes2020.xyz"
            client.removeUser(to)
            if client.connect():
                client.process(block=True)
                print("Done")
            else:
                print("Unable to connect.")
    