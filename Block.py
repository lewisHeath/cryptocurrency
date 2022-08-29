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

    @staticmethod
    def from_json(json_data):
        index = json_data['index']
        timestamp = json_data['timestamp']
        data = [Transaction.from_json(json_data=transaction) for transaction in json_data['data']]
        previous_hash = json_data['previous_hash']
        nonce = json_data['nonce']
        hash = json_data['hash']
        block = Block(index, data, previous_hash, nonce)
        block.hash = hash
        block.timestamp = timestamp
        return block
