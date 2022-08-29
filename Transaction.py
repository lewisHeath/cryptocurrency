# a class that represents a transaction in the blockchain
import hashlib


class Transaction:

    def __init__(self, sender, receiver, amount, signature):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.signature = signature

    def __str__(self):
        return f'{self.sender} -> {self.receiver} : {self.amount} | {self.signature}'

    def to_json(self):
        return {
            'sender': self.sender,
            'receiver': self.receiver,
            'amount': self.amount,
            'signature': self.signature
        }

    @staticmethod
    def from_json(json_data):
        sender = json_data['sender']
        receiver = json_data['receiver']
        amount = json_data['amount']
        signature = json_data['signature']
        return Transaction(sender, receiver, amount, signature)

    def verify_signature(self, public_key):
        # decrypt the signature with the public key
        decrypted_signature = public_key.decrypt(self.signature)
        # create a hash of the transaction data
        transaction_hash = hashlib.sha256()
        transaction_hash.update(str(self.sender).encode('utf-8'))
        transaction_hash.update(str(self.receiver).encode('utf-8'))
        transaction_hash.update(str(self.amount).encode('utf-8'))
        # compare the hash with the decrypted signature
        return transaction_hash.hexdigest() == decrypted_signature
