# To be installed:
# Flask==0.12.2: pip install Flask==0.12.2
# Postman HTTP Client: https://www.getpostman.com/
# requests==2.18.4: pip install requests==2.18.4


# Importing the libraries
import datetime
import hashlib
import json
from threading import Thread
import time
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse
import sys
import click

# Importing the Blockchain class
from Blockchain import Blockchain
from Mempool import Mempool
from Transaction import Transaction

# Creating a web app
app = Flask(__name__)

# Creating a Blockchain
mempool = Mempool()
blockchain = Blockchain(mempool=mempool)

# Mining a new block
# @app.route('/mine_block', methods = ['GET'])
# def mine_block():
#     previous_block = blockchain.get_previous_block()
#     previous_proof = previous_block['proof']
#     proof = blockchain.proof_of_work(previous_proof)
#     previous_hash = blockchain.hash(previous_block)
#     block = blockchain.create_block(proof, previous_hash)
#     response = {
#         'message': 'Congratulations, you just mined a block!',
#         'index': block['index'],
#         'timestamp': block['timestamp'],
#         'proof': block['proof'],
#         'previous_hash': block['previous_hash']
#     }
#     return jsonify(response), 200

# Getting the full Blockchain
@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = blockchain.chain_to_json()
    return response, 200

# Checking if the blockchain is valid
@app.route('/is_valid', methods = ['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {
            'message': 'Blockchain is valid.'
        }
    else:
        response = {
            'message': 'Blockchain is not valid.'
        }
    return jsonify(response), 200

# adding a new transaction to the blockchain
@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    print(mempool.transactions)
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all(key in json for key in transaction_keys):
        return 'Some elements of the transaction are missing', 400

    # create a new transaction
    index = len(blockchain.chain)
    transaction = Transaction(json['sender'], json['receiver'], json['amount'])
    # add the transaction to the mempool class
    mempool.add_transaction(transaction)
    transactions_in_mempool = mempool.get_transactions()
    print(transactions_in_mempool)
    response = {
        'message': f'This transaction will probably be added to block {index}',
        'transactions': transactions_in_mempool
    }
    return response, 201

# Decentralizing the Blockchain
@app.route('/connect_node', methods = ['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "No node", 400
    for node in nodes:
        blockchain.add_node(node)
        print(nodes)
    response = {
        'message': 'All the nodes are now connected. The Koin Blockchain now contains the following nodes:',
        'total_nodes': list(blockchain.nodes)
    }
    return jsonify(response), 201

# Replacing the chain by the longest chain if needed
@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {
            'message': 'The nodes had different chains so the chain was replaced by the longest one.',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'All good. The chain is the largest one.',
            'actual_chain': blockchain.chain
        }
    return jsonify(response), 200

# Running the app
# @click.command()
# @click.option('--port', prompt='Port', help='Port to listen on')
def run(port_number):
    print(f'Listening on port {port_number}')
    app.run(host = '0.0.0.0', port = port_number)

def mine_blocks():
    while True:
        block = blockchain.create_block()
        print(block.__str__())

# Using 2 threads, one mining and one listening for requests
if __name__ == '__main__':
    t1 = Thread(target=mine_blocks)
    t1.start()
    run(5000)