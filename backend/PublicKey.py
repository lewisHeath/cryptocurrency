# A class for the public key

class PublicKey:

    def __init__(self, key):
        self.key = key

    def decrypt(self, signature):
        # use the key to decrypt the signature
        return self.key.decrypt(signature)
