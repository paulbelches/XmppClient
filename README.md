# XMPP Client

The project consists of implementing a client that supports the XMPP protocol.

A Xmpp client implementation in python.

## Dependencies 

* pkg-resources==0.0.0
* pyasn1==0.3.6
* pyasn1-modules==0.1.5
* sleekxmpp==1.3.3

## Setup and running

1. Clone repo `https://github.com/paulbelches/XmppClient`<br />
3. Run `pip install -r requirements.txt` to install dependencies.<br />
4. Run `main.py` to start the program <br />

## Functionalities

1.  Log in                                     
2.  Sign up                                     
3.  Show all registered users                   
4.  Show all contacts with their state          
5.  Add user to roster                          
6.  Show user info                              
7.  Direct message                              
8.  Group message                             
9.  Define presence                             
10.  Send notification                           
11.  Join group                                  
12. Send File                                   
13. Create group                                
14. Delete account                              
15. Log off
16. Handle online notifications 
17. Handle offline notifications 
18. Handle change status notification

## Usage

After running the programan, a menu with the current avalible options is display. Press the number of the option you wish to execute, and then enter. In case some input is required, the program will ask for it. 

## How to send files

To test the file transfer run 2 instances of the client. Then login in both of them, and choose from one of your clients option 12. Enter the file route (recomended) or use the testing image, and enter the other client username. The file will be saved in the client file location, with a number as name. 

## References

* https://github.com/fritzy/SleekXMPP/wiki/Event-Index
* https://github.com/fritzy/SleekXMPP/wiki/Stanzas:-Message
* https://sleekxmpp.readthedocs.io/en/latest/api/basexmpp.html
* https://gist.github.com/joelrebel/a54132c2151cd887b1d96b973a2de290
* https://xmpp.org/extensions/xep-0045.html#createroom
* https://xmpp.org/extensions/xep-0085.html
* https://gist.github.com/joelrebel/a54132c2151cd887b1d96b973a2de290
* https://xmpp.org/extensions/xep-0077.html#usecases-cancel

## License

Mit License Copyright (c) 2020 Paul Belches
