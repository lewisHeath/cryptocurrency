# a class that represents a blockchain

import requests
from urllib.parse import urlparse

from Mempool import Mempool
from Block import Block
from Transaction import Transaction
from Wallet import Wallet


class Blockchain:

    # constructor for the class
    def __init__(self, mempool):
        self.port = None
        self.ip = None
        self.node_address = None
        self.chain = []
        self.mempool = mempool
        self.nodes = set()
        self.mining_difficulty = 4
        self.wallet = Wallet()
        self.genesis_block()
        self.generate_keys_for_self()

    def generate_keys_for_self(self):
        self.wallet.generate_keys()
        # print the keys to the screen
        print(f'Public key: {self.wallet.public_key.to_string().hex()}')
        print(f'Private key: {self.wallet.private_key.to_string().hex()}')

    def add_initial_nodes(self):
        self.node_address = f'http://{self.ip}:{self.port}'
        nodes = requests.get('http://178.79.155.227/nodes')
        nodes = nodes.json()
        for node in nodes:
            # if the node is not this node, add it to the nodes list)
            if node != self.node_address:
                print('Adding node:', node)
                self.add_node(node)

        requests.post('http://178.79.155.227/nodes', json={'node': f'{self.ip}:{self.port}'})
        # self.sync_chain()

    def sync_chain(self):
        for node in self.nodes:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                chain = response.json()

                self.receive_chain(chain)
                return True
        return False

    def genesis_block(self):
        self.chain.append(Block(index=0, data=[], previous_hash='0', nonce=0))

    # creating a block
    def create_block(self):
        # get the previous block
        previous_block = self.get_previous_block()
        # set the nonce to 0
        nonce_value = 0
        # make transaction from nothing to the miners address
        from_address = '0'
        to_address = self.wallet.public_key.to_string().hex()
        amount = 10
        transaction_json = {
            'from_address': from_address,
            'to_address': to_address,
            'amount': amount
        }
        signature = self.wallet.sign_transaction(transaction_json, self.wallet.private_key.to_string().hex())
        miner_transaction = Transaction('0', to_address, amount, signature)
        # keep trying to make a block until you get a valid one
        while True:
            # print(f'Trying nonce value {nonce_value}')
            # check the chain has not been replaced
            previous_block_check = self.get_previous_block()
            if previous_block != previous_block_check:
                nonce_value = 0
            # get the previous block's hash
            previous_hash = previous_block_check.hash
            # get transactions from the mempool class, max 10 transactions
            transactions = self.mempool.transactions[:10]
            # add the miner transaction to the list of transactions at the start
            transactions.insert(0, miner_transaction)
            # create a block with the transactions
            block = Block(index=len(self.chain), data=transactions, previous_hash=previous_hash, nonce=nonce_value)
            # print(f'Block checking: {block.__str__()}')
            # print(block.hash, end='\r')
            # if the block is valid, add it to the chain
            if self.check_hash(block):
                self.chain.append(block)
                print(f'\nBlock #{block.index} has been added to the chain')
                # print(transactions)
                # remove the transactions from the mempool class
                # if the transactions list is not empty, remove the transactions from the mempool class
                if transactions:
                    self.remove_transactions(transactions)
                return block
            # otherwise, increment the nonce value and try again
            nonce_value += 1

    def check_hash(self, block):
        block_hash = block.hash
        # convert the hex string to a decimal number
        block_hash_decimal = int(block_hash, 16)
        length = len(self.nodes)
        if length == 0:
            length = 1
        # difficulty is 0x00000000FFFF0000000000000000000000000000000000000000000000000000 - the length of the nodes set
        target = 4744950587707503895717550246644061521101535778011892856149550039040000 / length
        # check if the decimal number is less than the target
        if block_hash_decimal < target:
            return True
        return False

    def remove_transactions(self, transactions):
        for transaction in transactions:
            # ignore the first transaction, which is the miner transaction
            if transaction != transactions[0]:
                print(f'Transaction #{transaction.__str__()} has been removed from the mempool')
                self.mempool.remove_transaction(transaction)

    # getting the last block on the chain
    def get_previous_block(self):
        return self.chain[-1]

    @staticmethod
    def is_chain_valid(chain):
        # print(chain)
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            # print('PRINTING BLOCK')
            # print(block)
            if block.previous_hash != previous_block.hash:
                return False
            previous_block = block
            block_index += 1
        return True

    def add_node(self, address):
        parsed_url = urlparse(address)
        print(parsed_url)
        self.nodes.add(parsed_url.netloc)
        # for node in self.nodes:
        #     print(node)

    def delete_node(self, node_address):
        self.nodes.discard(node_address)

    def connect_to_other_nodes(self):
        for node in self.nodes:
            try:
                requests.post(f'http://{node}/connect_node', json={'node': f'http://{self.ip}:{self.port}'})
            except requests.exceptions.ConnectionError:
                print(f'Node {node} is not online')
                continue

    def add_block(self, block):
        # turn the block out of a json object
        block = Block.from_json(block)
        self.chain.append(block)

    def receive_chain(self, chain):
        length = len(chain['chain'])
        # print(f'Received a chain of length {length} ---------------')
        if length > len(self.chain):
            # convert from json to a list of blocks
            # print(chain)
            new_chain = []
            chain = chain['chain']
            for block in chain:
                # print(f'checking block ----- {block}')
                new_block = Block(0, [], '0', 0)
                actual_block = Block.from_json(new_block, block)
                new_chain.append(actual_block)
            # check if the chain is valid
            if self.is_chain_valid(new_chain):
                # print('The chain is valid')
                # replace the current chain with the new one
                self.chain = new_chain
                print('THE CHAIN HAS BEEN REPLACED')
                return True
        else:
            print('The chain is not long enough')
            return False
        print('The chain is not valid')
        return False

    # def replace_chain(self):
    #     network = self.nodes
    #     longest_chain = None
    #     max_length = len(self.chain)
    #     for node in network:
    #         response = requests.get(f'http://{node}/get_chain')
    #         if response.status_code == 200:
    #             length = response.json()['length']
    #             chain = response.json()['chain']
    #             if length > max_length and self.is_chain_valid(chain):
    #                 max_length = length
    #                 longest_chain = chain
    #     if longest_chain:
    #         self.chain = longest_chain
    #         return True
    #     return False

    def chain_to_json(self):
        chain = []
        for block in self.chain:
            chain.append(block.to_json())

        chain_json = {
            'chain': chain,
            'length': len(self.chain)
        }
        return chain_json

    def get_wallet_balance(self, address):
        balance = 0
        for block in self.chain:
            for transaction in block.data:
                if transaction.sender == address:
                    balance -= transaction.amount
                if transaction.receiver == address:
                    balance += transaction.amount
        return balance