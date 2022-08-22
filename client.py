# saved as greeting-client.py
import Pyro5.api
import socket
import time
import numpy as np
import celtiCoin as cc
from threading import Thread


Pyro5.config.DETAILED_TRACEBACK = True

hostname = socket.gethostbyname(socket.gethostname()) + str(np.random.randint(0,100000000))

connection = Pyro5.api.Proxy("PYRONAME:connections")

connection.register = hostname
# poppedNode = connection.register

@Pyro5.api.expose
class MiningServer(object):

    def __init__(self):
        self._knownPeers = []
        self._blockchain = cc.Blockchain().__dict__
        self._hostname = hostname
        self._txnmempool = cc.TxnMemoryPool([]).__dict__
        self._announced = []

    @property
    def announced(self):
        return self._announced
    
    @announced.setter
    def announced(self, transHash):
        print("Echoing:", transHash)
        self._announced.append(transHash)

    @property
    def txnmempool(self):
        return self._txnmempool

    @txnmempool.setter
    def txnmempool(self, trans):
        self._txnmempool['transactions'].append(trans)

    
    def addTransaction(self):
        time.sleep(np.random.randint(3, 10))
        letters = list("abcdefghijklmnopqrstuvwxyz")
        rand = np.random.choice(letters).encode("utf-8")
        timeStamp = str(time.time()).encode("utf-8")
        trans = cc.Transaction(1, 1, [cc.hexlify(cc.sha256(rand + timeStamp).digest())], 1, [cc.Output(0,0, "none").__dict__]).__dict__
        # self.txnmempool.addTransaction(trans)
        #self.txnmempool['transactions'].append(trans)
        txnmempool = trans
        # self.announce(trans)
        return trans

    def announce(self, trans):
        previous = self._announced
        if trans['transactionHash'] not in previous:
            for i in self.knownPeers:
                announcer = Pyro5.api.Proxy("PYRONAME:" + i)
                if announcer.txnmempool == []:
                    announcer.txnmempool = trans
                    #announcer.announced = trans['transactionHash']
                elif trans['transactionHash'] not in [y['transactionHash'] for y in announcer.txnmempool['transactions']]:
                    announcer.txnmempool = trans
                    #announcer.announced = trans['transactionHash']



                if trans['transactionHash'] not in announcer.announced:
                    announcer.announced = trans['transactionHash']
                    announcer.announce(trans) #recursive transaction announcement
                    

    @property
    def hostname(self):
        return self._hostname

    @property
    def blockchain(self):
        return self._blockchain

    @property
    def knownPeers(self):
        return self._knownPeers

    #this is the hanshake method
    @knownPeers.setter
    def knownPeers(self, handshakeStruct):
        if handshakeStruct["addrMe"] not in self._knownPeers:
            print("handshake between: ", hostname, handshakeStruct["addrMe"])
            self._knownPeers.append(handshakeStruct["addrMe"])

miningServer = MiningServer()
daemon = Pyro5.api.Daemon()
ns = Pyro5.api.locate_ns()            
uri = daemon.register(miningServer)
ns.register(hostname, uri)
Thread(target=daemon.requestLoop).start()


#listening for new connections on the first node!
poppedNode = connection.register
while poppedNode == []:
    time.sleep(1) #not trying to blow up my kernel
    poppedNode = connection.register
    print("searching for connections")

while poppedNode[0]["addrMe"] == hostname:
    poppedNode = connection.register
    time.sleep(1)
    print("searching for secondary connections...")

if poppedNode != []:
    handshake = Pyro5.api.Proxy("PYRONAME:" + poppedNode[0]["addrMe"])
    time_ = time.time()
    height = len(miningServer.blockchain['blockList']) - 1
    #the syntax from pyro is a little wonky but here is the handshake maneuver
    handshake.knownPeers = {"nVersion":1, 
                            "nTime":time_, 
                            "addrMe":hostname,
                            "bestHeight":height}
    miningServer.knownPeers = {"nVersion":1,
                            "nTime":time_, 
                            "addrMe":handshake.hostname,
                            "bestHeight":height}
    otherNodesKnownPeers = handshake.knownPeers
    for i in otherNodesKnownPeers:
        if i != hostname:
            handshake = Pyro5.api.Proxy("PYRONAME:" + i)
            handshake.knownPeers = {"nVersion":1, 
                                    "nTime":time_, 
                                    "addrMe":hostname,
                                    "bestHeight":height} 

#the DNS server sends the all clear after is has registered 3 nodes
#he said this was our call on how to implement
clearedToMine = False
while not clearedToMine:
    num = connection.checkNum()
    time.sleep(1) #no reason to make a thousand calls a second and freeze a container!
    if  num >= 3:
        clearedToMine = True

print("ready to mine!")
# daemon.requestLoop()

def discBroad():

    while True:
        #discover
        trans = miningServer.addTransaction()

        #broadcast
        print("New Transaction Discovered: ", trans['transactionHash'])
        miningServer.announce(trans)

Thread(target = discBroad()).start()














