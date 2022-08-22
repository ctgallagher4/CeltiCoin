#celticoin

from hashlib import sha256
from binascii import hexlify, unhexlify
import time
import numpy as np

class HashObject:
    '''An object to store hashes'''
    def __init__(self, *args):
        '''A method to initialize a Hash Object.'''
        intermediateList = self.unpack(args)
        intermediateHashable = ""
        for item in intermediateList:
            if type(item) == str:
                item = item.encode('utf-8')
            intermediateHashable += str(item)[2:-1]
        self.hash = self.doubleHash(intermediateHashable.encode("utf-8"))

    @staticmethod
    def doubleHash(hashable):
        '''
            A method to double sha256 some hashable data.
            Inputs: hashable (something which is hashable)
            Outputs: the hashed data
        '''
        return hexlify(sha256(sha256(hashable).digest()).digest())

    def __repr__(self):
        '''Overloading the __repr__ operator for printing'''
        return str(self.hash)
    
    @staticmethod
    def unpack(args):
        '''
            A helper method for hashing
            Inputs: args (a list of arguments)
            Outputs: the unpacked arguments
            Notice: doubly nested dictionaries or lists will NOT unpack
        '''
        unpacked = []
        for i in args:
            if type(i) == list or type(i) == tuple:
                unpacked.extend(i)
            elif type(i) == dict:
                unpacked.extend(i.values())
            else:
                unpacked.append(i)
        return unpacked

class Output:

    '''A class to handle transaction Outputs'''

    def __init__(self, value, index, script):
        '''Overloading the initialization.'''
        self.value = value
        self.index = index
        self.script = script

    def __repr__(self):
        '''Overloading the representation.'''
        return f"{self.value} : {self.index} : {self.script}"

class Transaction:
    '''A class for holding transactions'''
    def __init__(self, versNum: int, inCount: int, lOI: list, oC: int, lOO: list):
        '''Overloading the initialization'''
        self.versionNumber = versNum
        self.inCounter = inCount
        self.listOfInputs= lOI
        self.outCounter = oC
        self.listOfOutputs = lOO
        self.transactionHash = HashObject(versNum, inCount, lOI, oC, lOO).hash

    def printTransaction(self):
        '''A method to print a transaction'''
        print("Version Number:", self.versionNumber)
        print("In Counter:", self.inCounter)
        print("List of Inputs:")
        for count, input in enumerate(self.listOfInputs):
            print("  ", str(count) + ":", input)
        print("Out Counter:", self.outCounter)
        print("List of Outputs:")
        for count, output in enumerate(self.listOfOutputs):
            print("  ", str(count) + ":", output)
        print("Transaction Hash:", self.transactionHash)

class Header:
    '''A class for holding a header'''
    def __init__(self, prevBlock: HashObject or bytes, hashMerkleRoot: HashObject):
        '''Overloading the initialization.'''
        self.Version = 1
        self.hashPrevBlock = prevBlock
        self.hashMerkleRoot = hashMerkleRoot
        self.timestamp = time.time() # seconds since a time in 1970
        #self.bits = "0x207fffff"
        #self.bits = '0x1d00ffff' # the other option
        self.bits = "0x1e200000"
        # The instructions say "If you have no immediate need for a given 
        # element (for instance, a Block's Nonce or Bits values), you can 
        # simply leave them with a default value for the time being.  
        # Again, default values should be set at the time of object 
        # instantiation." Therefore these are left as 0 for now by default
        self.Nonce = 0

    def printHeader(self):
        '''A method to print a header'''
        print("Previous Block:", self.hashPrevBlock)
        print("Merkle Root:", self.hashMerkleRoot)

class Block:
    '''A class to hold a block'''
    def __init__(self, PrevBlockHash: HashObject or bytes, transactions: list):
        '''Overloading the initialization operator'''
        self.magicNumberString = "0xD9B4BEF9"
        self.magicNumberInt = 4190024921
        self.transactionCounter = len(transactions)
        self.transactions = transactions
        self.blockSize = 0 # set to 0 for now as per the instructions see above
        transactionHashes = [i.transactionHash for i in transactions]
        self.merkleTreeDict = self.buildMerkleTreeDict(transactionHashes)
        hashMerkleRoot = max(self.merkleTreeDict, key=self.merkleTreeDict.get)
        self.blockHeader = Header(PrevBlockHash, hashMerkleRoot)
        head = self.blockHeader
        self.blockHash = HashObject(head.timestamp, head.hashMerkleRoot,
                                    head.bits, head.hashPrevBlock).hash

    def printBlock(self):
        '''A method to print a block'''
        print("Transaction Counter:", self.transactionCounter)
        print("Transactions:")
        for transaction in self.transactions:
            transaction.printTransaction()
        print("Header:")
        self.blockHeader.printHeader()
        print("Block Hash:")
        print(self.blockHash)
        print("-----------------------END OF BLOCK--------------------------")

    @staticmethod
    def buildMerkleTreeDict(transactionsList: list) -> dict:
        '''
            This function takes in a transaction list and builds out a 
            dictionary of the complete Merkle tree.
            Inputs: transactionList (a list of transaction hashes)
            Outputs: merkleTreeDictionary (a merkle tree in the form of a dict)
        '''
        branches = transactionsList
        levelCount = 2
        merkleTreeDictionary = {}

        if len(branches) == 1:
            merkleTreeDictionary[branches[0]] = 1
            return merkleTreeDictionary

        for item in branches:
            if type(item) != bytes:
                merkleTreeDictionary[item.encode('utf-8')] = 1
            else:
                merkleTreeDictionary[item] = 1
            
        while len(branches) > 1:
            nextLevelBranches = []
            for i in range(0, len(branches), 2):
                val = branches[i]
                if i + 1 < len(branches):
                    branchHash = HashObject(val, branches[i+1]).hash
                    nextLevelBranches.append(branchHash)
                else:
                    branchHash = HashObject(val, val).hash
                    nextLevelBranches.append(branchHash)
                merkleTreeDictionary[branchHash] = levelCount
            levelCount += 1
            branches = nextLevelBranches

        return merkleTreeDictionary
   
class Blockchain():
    '''A class to hold multiple blocks'''
    def __init__(self):#, blockList):
        prevGenBlockHash = b"0000000000000000000000000000000000000000000000000000000000000000"
        genTransactions = [Transaction(1, 1, ["Adam"], 1, ["Eve"])]
        genesis = Block(prevGenBlockHash, genTransactions)
        self.blockList = [genesis] #+ blockList
        self.MAX_TXNS = 10

    def appendBlock(self, block):
        '''adding a block to our blockchain'''
        self.blockList.append(block)

    def findBlock(self, blockHeight = None, blockHash = None):
        '''
            A method to find a block given a blockHeight or BlockHash
            Inputs: blockHeight or blockHash
            Outputs: the found block or none if not found
            Note: defaults to blockHeight if two parameters given
        '''
        if blockHeight != None and blockHash == None:
            return self.blockList[blockHeight]

        elif blockHeight == None and blockHash != None:
            for block in self.blockList:
                if block.blockHash == blockHash:
                    return block
            return None

    def findTransaction(self, transactionHash):
        '''
            A method to find a transaction given a transaction hash
            Inputs: transactionHash 
            Outputs: the found transaction or none if not found
        '''
        for block in self.blockList:
            for transaction in block.transactions:
                if transaction.transactionHash == transactionHash:
                    return transaction

class Miner:

    '''A class to handle mining our blockchain'''
    
    @staticmethod
    def mine(txnMemoryPool, blockChain):
        '''
            A method to mine a transaction pool:
            Inputs: txnMemoryPool - a TxnMemoryPool object
                    blockChain - a Blockchain object
            Outputs: none
        '''
        count = 0
        MAX = blockChain.MAX_TXNS

        #we remove transactions from the memory pool as we go
        while len(txnMemoryPool.transactions) != 0:

            #getting the oldest transactions available assuming FIFO
            transactions = []
            if len(txnMemoryPool.transactions) > MAX - 1:
                #grab the first few transactions
                transactions.extend(txnMemoryPool.transactions[0:MAX])
                #remove them from the list
                txnMemoryPool.transactions = txnMemoryPool.transactions[MAX:]
            else:
                #grabbing the remaining transactions
                transactions.extend(txnMemoryPool.transactions)
                #remove them from the list
                txnMemoryPool.transactions = []

            #Create a block step (POW)
            coinBaseTransaction = [Transaction(1, 0, [], 1, [Output(50000, 1, "myScriptToMe")])]
            prevBlockHash = blockChain.blockList[count].blockHash
            attemptedBlock = Block(prevBlockHash, transactions + coinBaseTransaction)
            attemptedBlockHashInt = int(attemptedBlock.blockHash, base=16)
            exponent = unhexlify(attemptedBlock.blockHeader.bits[2:4])[::-1] #convert endianness
            coefficient = unhexlify(attemptedBlock.blockHeader.bits[4:])[::-1] #convert endianness
            coefficient = int(hexlify(coefficient), base=16)
            exponent = int(hexlify(exponent), base=16)
            
            target = coefficient * 2 ** (8 * (exponent - 3))
            
            #if the created blockHash is not less than target, then keep trying until it is
            while attemptedBlockHashInt > target:
                attemptedBlock = Block(prevBlockHash, transactions + coinBaseTransaction)
                attemptedBlockHash = attemptedBlock.blockHash
                attemptedBlockHashInt = int(attemptedBlockHash, base=16)

            #append the successful block to the blockchain
            blockChain.appendBlock(attemptedBlock)
            count += 1
        
class TxnMemoryPool():

    '''A class to handle Transation Memory Pools.'''

    def __init__(self, listOfTransactionObjects):
        '''Overriding the initialization.'''
        self.transactions = listOfTransactionObjects
    
    def addTransaction(self, transactionObject):
        '''A method to add transactions to our memory pool'''
        self.transactions.append(transactionObject)

    def removeTransaction(self):
        '''A method to remove a transaction from our memory pool'''
        removed = self.transactions.pop(0)
        return removed


def main():

    '''A main function to execute step3 test.'''

    letters = list("abcdefghijklmnopqrstuvwxyz")

    #generating 91 transactions
    transactions91 = []
    for i in range(91):
        rand = np.random.choice(letters).encode("utf-8")
        timeStamp = str(time.time()).encode("utf-8")
        transactions91.append(Transaction(1, 1, [hexlify(sha256(rand + timeStamp).digest())], 1, [Output(0,0, "none")]))

    #creating a transaction memory pool
    txnMemPool = TxnMemoryPool(transactions91)

    #creating an empty blockchain (genesis block included)
    blockChain = Blockchain([])

    #begining to mine the transaction memory pool and add blocks to the blockchain
    Miner.mine(txnMemPool, blockChain)

    #implementing the test for step 3
    print(len(blockChain.blockList))

if __name__ == '__main__':
    main()
