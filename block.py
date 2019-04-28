import hashlib
import json
import time

class Empty:
    def __init__(self):
        self.everything = None

class Service:
    def __init__(self, amount, description, date, payee):
        self.rendered = False
        self.amount = amount
        self.date = date
        self.description = description
        self.timestamp = time.time()
        #self.payment = Payment(payee, payment_amount)
        self.payee = payee
        self.nonce = 0
    def confirm(self):
        self.rendered = True

class Payment:
    def __init__(self, payee, amount):
        self.payer = 'charity'
        self.payee = payee
        self.amount = amount
        self.timestamp = time.time()
        self.nonce = 0

class Block:
    def __init__(self, index, transactions, timestamp, previous_hash):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
    def compute_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.unconfirmed_transactions = [] # data yet to get into blockchain
        self.chain = []
        self.create_genesis_block()
        self.difficulty = 2
    def create_genesis_block(self):
        genesis_block = Block(0, [], time.time(), "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)
    @property
    def last_block(self):
        return self.chain[-1]
    def proof_of_work(self, data):
        data.nonce = 0
        computed_hash = data.compute_hash()
        while not computed_hash.startswith('0' * self.difficulty):
            data.nonce += 1
            computed_hash = data.compute_hash()
        return computed_hash
    def add_block(self, data, proof):
        """
        A function that adds the block to the chain after verification.
        """
        previous_hash = self.last_block.hash
        if previous_hash != data.previous_hash:
            return False
        if not self.is_valid_proof(data, proof):
            return False
        data.hash = proof
        self.chain.append(data)
        return True
    def is_valid_proof(self, data, data_hash):
        """
        Check if block_hash is valid hash of block and satisfies
        the difficulty criteria.
        """
        return (data_hash.startswith('0' * self.difficulty) and
                data_hash == data.compute_hash())
    def add_new_transaction(self, transaction):
            self.unconfirmed_transactions.append(transaction)
    def mine(self):
        """
        This function serves as an interface to add the pending
        transactions to the blockchain by adding them to the block
        and figuring out Proof of Work.
        """
        if not self.unconfirmed_transactions:
            return False
        last_block = self.last_block
        new_block = Block(index=last_block.index + 1,
                          transactions=self.unconfirmed_transactions,
                          timestamp=time.time(),
                          previous_hash=last_block.hash)
        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)
        self.unconfirmed_transactions = []
        return new_block.index
    def get_blocks(self):
        return self.chain

class Payee: #find out from abby how payer's identified
    def __init__(self, first_name, last_name):
        self.first
