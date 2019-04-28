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

