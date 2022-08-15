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
import click
from signal import SIGTERM, signal, SIGINT
from sys import exit

# Importing the Blockchain class
from Blockchain import Blockchain
from Mempool import Mempool
from Transaction import Transaction

# Creating a web app
app = Flask(__name__)

# Creating a Blockchain
mempool = Mempool()
blockchain = Blockchain(mempool=mempool)

# global variables
can_mine = False
global_port = 0

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

    # relay the transaction to all the nodes
    for node in blockchain.nodes:
        url = f'{node}/add_transaction'
        requests.post(url, json = json)

    return response, 201

@app.route('/receive_transaction', methods = ['POST'])
def receive_transaction():
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
    node = json.get('node')
    if node is None:
        return "No node", 400
    print(f'Adding node {node}')
    blockchain.add_node(node)
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

@app.route('/receive_chain', methods = ['POST'])
def receive_chain():
    print('RECEIVING CHAIN')
    json = request.get_json()
    chain = json.get('chain')
    print(chain['chain'])
    # print type of chain
    print(type(chain))
    if chain is None:
        return "No chain", 400
    valid = blockchain.receive_chain(chain)
    if valid:
        return "Chain is valid", 200
    else:
        return "Chain is not valid", 200

# Running the app
@click.command()
@click.option('--port', prompt='Port', help='Port to listen on')
def run(port):
    print(f'Listening on port {port}')
    global global_port
    global_port = port
    blockchain.port = port
    blockchain.add_initial_nodes(f'localhost:{port}')
    blockchain.connect_to_other_nodes()
    global can_mine
    can_mine = True
    app.run(host = '0.0.0.0', port = port)

def mine_blocks():
    while True:
        if can_mine:
            block = blockchain.create_block()
            # broadcast the new block to all the nodes
            for node in blockchain.nodes:
                url = f'http://{node}/receive_chain'
                # print(url)
                requests.post(url, json = {'chain': blockchain.chain_to_json()})
            print(block.__str__())

def handler(signal_received, frame):
    # Handle any cleanup here
    # print('Received signal: {}'.format(signal_received))
    # send post request to delete this node from the list of nodes
    # print(f'Deleting node localhost:{global_port}')
    response = requests.delete(f'http://178.79.155.227/nodes/localhost:{global_port}')
    print(response.json())
    print('Exiting gracefully')
    exit(0)

# Using 2 threads, one mining and one listening for requests
if __name__ == '__main__':

    signal(SIGINT, handler)

    t1 = Thread(target=run)
    t1.daemon = True
    t1.start()
    # run()
    mine_blocks()