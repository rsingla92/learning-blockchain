"""
Tutorial: https://medium.com/crypto-currently/lets-make-the-tiniest-blockchain-bigger-ac360a328f4d
Issue 1: consensus function not used in tutorial.
Issue 2: error with unresolved variable.

The last RohitCoin has so simple it was almost useless.

1)There was no distribution, and no decentralization.
2) Blocks could only be added as fast as the host computer could create
    a block.

Let's refine the data field to be transactions. A transaction will be
a JSON object with the sender, receiver and amount of coin.

"""

from flask import Flask
from flask import request
import json
import requests
import hashlib as hasher
import datetime as date
node = Flask(__name__)

''' 
Tutorial: https://medium.com/crypto-currently/lets-build-the-tiniest-blockchain-e70965a248b

 A class describing what each block in our database for blockchain looks like.
 By definition, each block requires a timestamp to reflect when it was added
 to the blockchain. It has an optional index, but we'll use indices regardless
 for now.

 It also has a hash for identification and integrity purposes. 

 There is, of course, the data itself as well.

 Each block requires information about the previous block, forming a chain.
'''


class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.hash_block()

    def hash_block(self):
        sha = hasher.sha256()
        sha.update(str(self.index) +
                   str(self.timestamp) +
                   str(self.data) +
                   str(self.previous_hash)
                   )
        return sha.hexdigest()

''' 
    Create the initial block in the chain.
    Construct a block with index zero and arbitrary previous hash
'''
def create_rohitcoin_genesis_block():
    return Block(0, date.datetime.now(), {"proof-of-work": 29, "transactions": None}, "0")


def create_next_block(last_block):
    this_index = last_block.index + 1
    this_timestamp = date.datetime.now()
    this_data = "Block ID: " + str(this_index)
    this_hash = last_block.hash

    return Block(this_index, this_timestamp, this_data, this_hash)


miner_address = "rohit-is-a-miner"

# Genesis of RohitCoin
blockchain = []
blockchain.append(create_rohitcoin_genesis_block())
this_nodes_transactions = []
peer_nodes = []
isMining = True

'''
Let's create a HTTP server so users can send notifications to our nodes.
Nodes will accept POST requests (hence why the JSON formatting is useful)
'''


@node.route('/txion', methods=['POST'])
def transaction():
    if request.method == 'POST':
        # Extract the transaction data from the POST request
        new_txion = request.get_json()
        this_nodes_transactions.append(new_txion)

        # Log it to console
        print("New transaction received")
        print("\tFROM: %s" % new_txion['from'])
        print("\tTO: %s" % new_txion['to'])
        print("\tAMT: %s" % new_txion['amount'])
        return "Transaction successful"

@node.route('/mine', methods=['GET'])
def mine():
    if request.method == 'GET':
        # Where's the proof of work?
        last_block = blockchain[len(blockchain)-1]
        last_proof = last_block.data['proof-of-work']

        # Find proof of work for current block being mined.
        proof = proof_of_work(last_proof)

        # If valid, then mine a block and reward the miner!
        this_nodes_transactions.append({"from": "network", "to": miner_address, "amount": 1})

        new_block_data = {
                            "proof-of-work": proof,
                            "transactions": list(this_nodes_transactions)
                          }

        new_block_index = last_block.index + 1
        new_block_timestamp = date.datetime.now()
        last_block_hash = last_block.hash

        # Clear up the transactions list
        this_nodes_transactions[:] = []

        # New mined block
        new_block = Block(new_block_index, new_block_timestamp, new_block_data, last_block_hash)

        blockchain.append(new_block)

        return json.dumps({
                            "index" : new_block_index,
                            "timestamp" : str(new_block_timestamp),
                            "data": new_block_data,
                            "hash": last_block_hash
                            })


@node.route('/blocks', methods=['GET'])
def get_blocks():
    chain_to_send = blockchain
    for block in chain_to_send:
        block_index = str(block.index)
        block_timestamp = str(block.timestamp)
        block_data = str(block.data)
        block_hash = block.hash
        chain_to_send[block] = {
            "index": block_index,
            "timestamp": block_timestamp,
            "data": block_data,
            "hash": block_hash
        }
    chain_to_send = json.dumps(chain_to_send)
    return chain_to_send


def find_new_chains():
    other_chains = []
    for node_url in peer_nodes:
        # GET the nodes' chains and convert to Python dict
        block = requests.get(node_url + "/blocks").content
        block = json.loads(block)

        other_chains.append(block)
    return other_chains


def consensus():
    other_chains = find_new_chains()
    longest_chain = blockchain
    for chain in other_chains:
        if len(longest_chain) < len(chain):
            longest_chain = chain
    blockchain = longest_chain


'''
Where do people get RohitCoin though? People have to mine new blocks
    of RohitCoin. A successful miner gets it. 

    An algorithm that generates an item that is difficult to create but
    easy to verify is referred to as a Proof-of-Work algorithm.
'''


def proof_of_work(last_proof):
    # Create a variable to find the next proof of work
    incrementor = last_proof + 1

    while not ( incrementor % 29 == 0 and incrementor % last_proof == 0):
        incrementor += 1

    # Return the number that is representative of our work done
    return incrementor


'''
    This now lets users record when they've sent RohitCoin to each other.
    All transactions are stored for all to see and are stored on every
    node in the network.
'''
node.run()







