# a class to represent a wallet

from ecdsa import SigningKey, SECP256k1, VerifyingKey, BadSignatureError
from hashlib import sha256


class Wallet:

    def __int__(self):
        self.private_key = None
        self.public_key = None

    def generate_keys(self):
        self.private_key = SigningKey.generate(curve=SECP256k1)
        self.public_key = self.private_key.get_verifying_key()

    def get_keys(self):
        return {
            'public_key': self.public_key.to_string().hex(),
            'private_key': self.private_key.to_string().hex()
        }

    @staticmethod
    def hash_transaction(transaction):
        from_address = transaction.get('from_address')
        to_address = transaction.get('to_address')
        amount = transaction.get('amount')
        encoded = bytes(from_address + to_address + str(amount), 'utf-8')
        transaction_hash = sha256(encoded).hexdigest()
        return transaction_hash

    @staticmethod
    def verify_signature(transaction, signature):
        public_key = transaction.get('from_address')
        public_key_object = VerifyingKey.from_string(bytes.fromhex(public_key), curve=SECP256k1)
        transaction_hash = Wallet.hash_transaction(transaction)
        try:
            public_key_object.verify(bytes.fromhex(signature), bytes.fromhex(transaction_hash))
            return True
        except BadSignatureError:
            return False

    @staticmethod
    def sign_transaction(transaction, private_key):
        private_key_object = SigningKey.from_string(bytes.fromhex(private_key), curve=SECP256k1)
        transaction_hash = Wallet.hash_transaction(transaction)
        signature = private_key_object.sign(bytes.fromhex(transaction_hash))
        return signature.hex()
