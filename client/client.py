import sys
import logging
import getpass
import base64
import sleekxmpp
from sleekxmpp.exceptions import IqError, IqTimeout
from sleekxmpp.xmlstream.stanzabase import ET, ElementBase

class Client(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)
        
        #Event hadlers trigger functions when a event happens
        self.add_event_handler("session_start", self.start)

        if self.connect():
            print("Sign in completed")
            self.process(block=False)
        else:
            print("Could not connect")
  
    def start(self, event):
        self.send_presence(pshow="chat", pstatus="Ready to start") #Establish intial presence 
        self.get_roster()
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
        except IqError as e:
            print(e)
            print("Could not remove account")
            self.disconnect()
        except IqTimeout:
            print("Server did no respond")
            self.disconnect()
#====================================================================================0
import getpass 

client = Client("tonifake3@redes2020.xyz", "aaaa") 
input()
client.unregister()
print("Done")
         
    