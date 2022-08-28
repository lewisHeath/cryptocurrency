# a class for the pending transactions of the blockchain
from Transaction import Transaction


class Mempool:

    def __init__(self):
        self.transactions = []

    def add_transaction(self, transaction):
        self.transactions.append(transaction)
        return self.transactions

    def remove_transaction(self, transaction):
        self.transactions.remove(transaction)
        return self.transactions

    def get_transactions(self):
        # return json representation of the transactions
        return [transaction.to_json() for transaction in self.transactions]

    def from_json(self, json):
        self.transactions = [Transaction.from_json(transaction) for transaction in json]
        return self.transactions

    def get_wallet_balance(self, address):
        balance = 0
        for transaction in self.transactions:
            if transaction.sender == address:
                balance -= transaction.amount
        return balance
