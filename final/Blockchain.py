# a class that represents a blockchain

import datetime
import hashlib
from hmac import trans_36
import json
import requests
from uuid import uuid4
from urllib.parse import urlparse

from Mempool import Mempool
from Block import Block


class Blockchain:
    
    # constructor for the class
    def __init__(self, mempool):
        self.chain = []
        self.mempool = mempool
        self.nodes = set()
        self.mining_difficulty = 5
        self.genesis_block()

    def genesis_block(self):
        self.chain.append(Block(index=0, data=[], previous_hash='0', nonce=0))

    # creating a block
    def create_block(self):
        # get the hash of the previous block
        previous_block = self.get_previous_block()
        previous_hash = previous_block.hash
        # set the nonce to 0
        nonce_value = 0
        # keep trying to make a block until you get a valid one
        while True:
            # get transactions from the mempool class, max 10 transactions
            transactions = self.mempool.transactions[:10]
            # create a block with the transactions
            block = Block(index = len(self.chain), data = transactions, previous_hash = previous_hash, nonce = nonce_value)
            print(block.hash, end='\r')
            # if the block is valid, add it to the chain
            if self.check_hash(block):
                self.chain.append(block)
                print(f'\nBlock #{block.index} has been added to the chain')
                print(transactions)
                # remove the transactions from the mempool class
                # if the transactions list is not empty, remove the transactions from the mempool class
                if transactions:
                    self.remove_transactions(transactions)
                return block
            # otherwise, increment the nonce value and try again
            nonce_value += 1

    def check_hash(self, block):
        block_hash = block.hash
        return block_hash[:self.mining_difficulty] == '0' * self.mining_difficulty

    def remove_transactions(self, transactions):
        for transaction in transactions:
            print(f'Transaction #{transaction.__str__()} has been removed from the mempool')
            self.mempool.remove_transaction(transaction)
        

    # getting the last block on the chain
    def get_previous_block(self):
        return self.chain[-1]

    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block.previous_hash != previous_block.hash:
                return False
            previous_block = block
            block_index += 1
        return True

    def add_node(self, address):
        parsed_url = urlparse(address)
        print(parsed_url)
        self.nodes.add(parsed_url.netloc)

    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False

    def chain_to_json(self):
        chain_json = {
            'chain': [block.to_json() for block in self.chain],
            'length': len(self.chain)
        }
        return chain_json

