from pickletools import markobject
import Pyro5.server
import socket
import Pyro5.api
import time

# Pyro5.config.SERVERTYPE = "multiplex"

#Note, the following code REQUIRES 'access methods' on the containing class to work.
#See this link for more information: https://github.com/irmen/Pyro4/issues/105

def getTime():
    return int(time.time())

def makeRegistration(hostname, time_):
    return {"nVersion": 1,
            "nTime": time_,
            "addrMe": hostname}


@Pyro5.server.expose
class Connections(object):

    def __init__(self):
        self.registrations = []
        self.IPs = []
 
    @property
    def register(self):
        return self.registrations[-2:-1] # we don't want to return the most recently added node
    
    @register.setter
    def register(self, val):
        time = getTime()
        val = makeRegistration(val, time)
        if val['addrMe'] in self.IPs:
            print("already added: ", val)
        else:
            print("adding: ", val)
            self.registrations.append(val)
            self.IPs.append(val['addrMe'])

    def checkNum(self):

        return len(self.registrations)

connections = Connections()

daemon = Pyro5.api.Daemon()
ns = Pyro5.api.locate_ns()            
uri = daemon.register(connections)
ns.register("connections", uri)

print("Ready.")      
daemon.requestLoop() 

