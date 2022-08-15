# a class that represents a transaction in the blockchain

class Transaction:

    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount

    def __str__(self):
        return f'{self.sender} -> {self.receiver} : {self.amount}'

    def to_json(self):
        return {
            'sender': self.sender,
            'receiver': self.receiver,
            'amount': self.amount
        }
    
    def from_json(self, json_data):
        self.sender = json_data['sender']
        self.receiver = json_data['receiver']
        self.amount = json_data['amount']
        return self