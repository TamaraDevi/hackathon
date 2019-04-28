from hashlib import sha256
import json
import time
from block import Block, Blockchain, Service, Payment
import run

from flask import Flask, request
import requests



app = Flask(__name__)

# the node's copy of blockchain
blockchain = Blockchain()
#blockchain.create_genesis_block()

# the address to other participating members of the network
peers = set()


# endpoint to submit a new transaction. This will be used by
# our application to add new data (posts) to the blockchain
# endpoint to return the node's copy of the chain.
# Our application will be using this endpoint to query
# all the posts to display.
@app.route('/', methods=['GET'])
def get_chain():

    # make sure we've the longest chains
    #form_post="<form action=\"/new_block_added\" method=\"post\">     <br>Identifier code:<br>    <input type=\"text\" =\"ID\" required>  <br>Received at<br>   <br>Date:<br>  <input type=\"Date\" name=\"date\">    <br>Location:<br>  <input type=\"text\" name=\"Location\">      <br><input type=\"submit\" value=\"Submit\" ><br>       </form>"
    form_post = """<form action=\"/new_block_added\" method=\"post\">
    <h1>Order:</h1>
    <br>Amount:<br>    <input type=\"text\" name=\"amount\" required>
    <br>Description:<br>    <input type=\"text\" name=\"description\" required>
    <br>Date:<br>    <input type=\"Date\" name=\"date\" required>
    <br>Seller:<br>    <input type=\"text\" name=\"seller\" required>
    <br><input type=\"submit\" value=\"Submit\" ><br></form>"""



    return "<div>"+form_post+"</div>"


@app.route('/service_provider', methods=['GET'])
def get_id():
    form_post = "<form action=\"/\" method=\"post\">"



@app.route('/new_block_added', methods=['POST'])

def add_our_block():



    amount=request.form.get('amount')
    description=request.form.get('description')
    date=request.form.get('date')
    seller=request.form.get('seller')

    service=Service(amount,description,date,seller)
    blockchain.add_new_transaction(json.dumps(service.__dict__, sort_keys=True))
    blockchain.mine()

    BC=blockchain.get_blocks()
    string = ''
    #<form><input type="button" value="Back"></form>
    for b in BC:
        string = "<div>"+string+ json.dumps(b.__dict__, sort_keys=True)+"</div>"
    return string








@app.route('/service_provider', methods=['POST'])
def service_provider():
    tx_data = request.get_json()
    required_fields = ["author", "content"]
    for field in required_fields:
        if not tx_data.get(field):
            return "Invalid transaction data", 404

    tx_data["timestamp"] = time.time()
    blockchain.add_new_transaction(tx_data)
    return "Success", 201


# endpoint to request the node to mine the unconfirmed
# transactions (if any). We'll be using it to initiate
# a command to mine from our application itself.
@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    result = blockchain.mine()
    if not result:
        return "No transactions to mine"
    return "Block #{} is mined.".format(result)


# endpoint to add new peers to the network.
@app.route('/register_node', methods=['POST'])
def register_new_peers():
    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400

    # Add the node to the peer list
    peers.add(node_address)

    # Return the consensus blockchain to the newly registered node
    # so that he can sync
    return get_chain()

@app.route('/register_with', methods=['POST'])
def register_with_existing_node():
    """
    Internally calls the `register_node` endpoint to
    register current node with the node specified in the
    request, and sync the blockchain as well as peer data.
    """
    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400

    data = {"node_address": request.host_url}
    headers = {'Content-Type': "application/json"}

    # Make a request to register with remote node and obtain information
    response = requests.post(node_address + "/register_node",
                             data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        global blockchain
        global peers
        # update chain and the peers
        chain_dump = response.json()['chain']
        blockchain = create_chain_from_dump(chain_dump)
        peers.update(response.json()['peers'])
        return "Registration successful", 200
    else:
        # if something goes wrong, pass it on to the API response
        return response.content, response.status_code


def create_chain_from_dump(chain_dump):
    blockchain = Blockchain()
    for idx, block_data in enumerate(chain_dump):
        block = Block(block_data["index"],
                      block_data["transactions"],
                      block_data["timestamp"],
                      block_data["previous_hash"])
        proof = block_data['hash']
        if idx > 0:
            added = blockchain.add_block(block, proof)
            if not added:
                raise Exception("The chain dump is tampered!!")
        else:  # the block is a genesis block, no verification needed
            blockchain.chain.append(block)
    return blockchain


# endpoint to add a block mined by someone else to
# the node's chain. The block is first verified by the node
# and then added to the chain.
@app.route('/add_block', methods=['POST'])
def verify_and_add_block():
    block_data = request.get_json()
    block = Block(block_data["index"],
                  block_data["transactions"],
                  block_data["timestamp"],
                  block_data["previous_hash"])

    proof = block_data['hash']
    added = blockchain.add_block(block, proof)

    if not added:
        return "The block was discarded by the node", 400

    return "Block added to the chain", 201


# endpoint to query unconfirmed transactions
@app.route('/pending_tx')
def get_pending_tx():
    return json.dumps(blockchain.unconfirmed_transactions)


def consensus():
    """
    Our simple consnsus algorithm. If a longer valid chain is
    found, our chain is replaced with it.
    """
    global blockchain

    longest_chain = None
    current_len = len(blockchain.chain)

    for node in peers:
        print('{}/chain'.format(node))
        response = requests.get('{}chain'.format(node))
        print("Content", response.content)
        length = response.json()['length']
        chain = response.json()['chain']
        if length > current_len and blockchain.check_chain_validity(chain):
            current_len = length
            longest_chain = chain

    if longest_chain:
        blockchain = longest_chain
        return True

    return False


def announce_new_block(block):
    """
    A function to announce to the network once a block has been mined.
    Other blocks can simply verify the proof of work and add it to their
    respective chains.
    """
    for peer in peers:
        url = "{}add_block".format(peer)
        requests.post(url, data=json.dumps(block.__dict__, sort_keys=True))
