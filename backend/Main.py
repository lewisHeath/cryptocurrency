# Importing the libraries
from threading import Thread
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS, cross_origin
import requests
import click
from signal import signal, SIGINT
from sys import exit

# Importing the Blockchain class
from Blockchain import Blockchain
from Mempool import Mempool
from Transaction import Transaction
from Wallet import Wallet

# Creating a web app
app = Flask(__name__, static_folder='../frontend/build/static')
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Creating a Blockchain
mempool = Mempool()
blockchain = Blockchain(mempool=mempool)

# global variables
can_mine = False
global_port = 0
global_ip = ''


# Default route
@app.route('/', methods=['GET'])
def default():
    # response = {
    #     'message': 'Welcome to the blockchain API!',
    #     'nodes': list(blockchain.nodes)
    # }
    # return jsonify(response), 200
    # serve a react app inside ../frontend/build
    return send_from_directory('../frontend/build', 'index.html')


# Getting the full Blockchain
@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = blockchain.chain_to_json()
    return response, 200


# Checking if the blockchain is valid
@app.route('/is_valid', methods=['GET'])
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
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    json = request.get_json()
    transaction_json = json.get('transaction')
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all(key in transaction_json for key in transaction_keys):
        return 'Some elements of the transaction are missing', 400

    # if there is not a signature property in json
    if 'signature' not in json:
        return 'No signature in the transaction', 400
    signature = json['signature']
    # if the signature is not valid
    if Wallet.verify_signature(transaction_json, signature) is False:
        return 'Invalid signature', 400

    # CHECK IF THE FROM ADDRESS HAS ENOUGH BALANCE - TODO
    wallet_balance = blockchain.get_wallet_balance(transaction_json['sender']) + mempool.get_wallet_balance(transaction_json['sender'])
    if wallet_balance < transaction_json['amount']:
        return 'Insufficient balance', 400

    # create a new transaction
    index = len(blockchain.chain)
    transaction = Transaction(json['sender'], json['receiver'], json['amount'], signature)
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
        url = f'{node}/receive_transaction'
        try:
            requests.post(url, json=json)
        except requests.exceptions.ConnectionError:
            continue

    return response, 201


@app.route('/receive_transaction', methods=['POST'])
def receive_transaction():
    json = request.get_json()
    transaction_json = json.get('transaction')
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all(key in transaction_json for key in transaction_keys):
        return 'Some elements of the transaction are missing', 400

    # if there is not a signature property in json
    if 'signature' not in json:
        return 'No signature in the transaction', 400
    signature = json['signature']
    # if the signature is not valid
    if Wallet.verify_signature(transaction_json, signature) is False:
        return 'Invalid signature', 400

    # CHECK IF THE FROM ADDRESS HAS ENOUGH BALANCE - TODO
    wallet_balance = blockchain.get_wallet_balance(transaction_json['sender']) + mempool.get_wallet_balance(transaction_json['sender'])
    if wallet_balance < transaction_json['amount']:
        return 'Insufficient balance', 400

    # create a new transaction
    index = len(blockchain.chain)
    transaction = Transaction(json['sender'], json['receiver'], json['amount'], signature)
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
@app.route('/connect_node', methods=['POST'])
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


# deleting a node from the list of nodes
@app.route('/delete_node', methods=['POST'])
def delete_node():
    json = request.get_json()
    node = json.get('node')
    if node is None:
        return "No node", 400
    print(f'Deleting node {node}')
    blockchain.delete_node(node)
    response = {
        'message': 'Deleted the node from the list of nodes.'
    }
    return jsonify(response), 201


# Replacing the chain by the longest chain if needed
@app.route('/replace_chain', methods=['GET'])
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


@app.route('/receive_chain', methods=['POST'])
def receive_chain():
    print('RECEIVING CHAIN')
    json = request.get_json()
    chain = json.get('chain')
    if chain is None:
        return "No chain", 400
    valid = blockchain.receive_chain(chain)
    if valid:
        return "Chain is valid", 200
    else:
        return "Chain is not valid", 200


@app.route('/receive_mempool', methods=['POST'])
def receive_mempool():
    print('RECEIVING MEMPOOL')
    json = request.get_json()
    transactions = json.get('transactions')
    if transactions is None:
        return "No transactions", 400
    mempool.from_json(transactions)
    return "Transactions received", 200


# generating wallet public keys and private keys
@app.route('/generate_wallet', methods=['GET'])
@cross_origin()
def generate_wallet():
    wallet = Wallet()
    wallet.generate_keys()
    keys = wallet.get_keys()
    response = {
        'public_key': keys['public_key'],
        'private_key': keys['private_key']
    }
    return jsonify(response), 200


# Running the app
@click.command()
@click.option('--port', prompt='Port', help='Port to listen on')
@click.option('--ip', prompt='Public IP', help='Public IP address')
def run(port, ip):
    print(f'Listening on port {port} and IP {ip}')
    global global_port
    global_port = port
    blockchain.port = port
    global global_ip
    global_ip = ip
    blockchain.ip = ip
    blockchain.add_initial_nodes()
    blockchain.connect_to_other_nodes()
    global can_mine
    can_mine = True
    app.run(host='0.0.0.0', port=port)


def mine_blocks():
    while True:
        if can_mine:
            block = blockchain.create_block()
            # broadcast the new block to all the nodes
            for node in blockchain.nodes:
                url = f'http://{node}/receive_chain'
                # print(url)
                requests.post(url, json={'chain': blockchain.chain_to_json()})
            # broadcast the new mempool to all the nodes
            for node in blockchain.nodes:
                url = f'http://{node}/receive_mempool'
                # print(url)
                try:
                    requests.post(url, json={'transactions': mempool.get_transactions()})
                except requests.exceptions.ConnectionError:
                    continue
            print(block.__str__())


# handle the CTRL + C event
def handler(signal_received, frame):
    # send post request to delete this node from the list of nodes
    response = requests.delete(f'http://178.79.155.227/nodes/{global_ip}:{global_port}')
    # tell all the nodes to delete this node from their list of nodes
    for node in blockchain.nodes:
        url = f'http://{node}/delete_node'
        try:
            requests.post(url, json={'node': f'{global_ip}:{global_port}'})
        except requests.exceptions.ConnectionError:
            continue
    if response.status_code == 200:
        print('Node deleted')
    print('Exiting gracefully...')
    exit(0)


# Using 2 threads, one mining and one listening for requests
if __name__ == '__main__':
    # CTRL C event
    signal(SIGINT, handler)
    # start the web server
    t1 = Thread(target=run)
    t1.daemon = True
    t1.start()
    # start the mining thread (main thread)
    mine_blocks()




