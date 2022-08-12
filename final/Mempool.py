# a class for the pending transactions of the blockchain

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