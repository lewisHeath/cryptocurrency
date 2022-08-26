# a class for a block in the blockchain

import hashlib
import time

from Transaction import Transaction


class Block:

    def __init__(self, index, data, previous_hash, nonce):
        self.index = index
        self.timestamp = time.time()
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.hash_block()

    def __str__(self):
        return f'Data: {self.data}, Previous Hash: {self.previous_hash}, Hash: {self.hash}'

    def hash_block(self):
        sha = hashlib.sha256()
        string = str(self.index) + str(self.timestamp) + str(self.data) + str(self.previous_hash) + str(self.nonce)
        sha.update(string.encode('utf-8'))
        return sha.hexdigest()
    
    def to_json(self):
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'data': [transaction.to_json() for transaction in self.data],
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'hash': self.hash
        }
    
    def from_json(self, json_data):
        self.index = json_data['index']
        self.timestamp = json_data['timestamp']
        self.data = [Transaction.from_json(transaction) for transaction in json_data['data']]
        self.previous_hash = json_data['previous_hash']
        self.nonce = json_data['nonce']
        self.hash = json_data['hash']
        return self