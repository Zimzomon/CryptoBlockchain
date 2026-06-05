import hashlib
import json
import time
import os

MINING_REWARD = 50


class Block:
    def __init__(self, index, timestamp, transactions, previous_hash, nonce=0):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        data = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)

        return hashlib.sha256(data.encode()).hexdigest()

    def mine(self, difficulty):
        target = "0" * difficulty

        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()


class Blockchain:

    def __init__(self):
        self.file_name = "blockchain.json"
        self.difficulty = 4
        self.pending_transactions = []

        if os.path.exists(self.file_name):
            self.load_chain()
        else:
            self.chain = [self.create_genesis_block()]
            self.save_chain()

    def create_genesis_block(self):
        return Block(0, time.time(), [], "0")

    def latest_block(self):
        return self.chain[-1]

    def get_balance(self, wallet):

        balance = 0

        for block in self.chain:
            for tx in block.transactions:

                if tx["from"] == wallet:
                    balance -= tx["amount"]

                if tx["to"] == wallet:
                    balance += tx["amount"]

        return balance

    def add_transaction(self, sender, receiver, amount):

        if sender != "SYSTEM":

            if self.get_balance(sender) < amount:
                print("Insufficient balance!")
                return False

        self.pending_transactions.append({
            "from": sender,
            "to": receiver,
            "amount": amount
        })

        return True

    def mine_pending_transactions(self, miner):

        self.pending_transactions.append({
            "from": "SYSTEM",
            "to": miner,
            "amount": MINING_REWARD
        })

        block = Block(
            len(self.chain),
            time.time(),
            self.pending_transactions,
            self.latest_block().hash
        )

        print("Mining...")
        block.mine(self.difficulty)

        self.chain.append(block)
        self.pending_transactions = []

        self.save_chain()

        print("Block mined successfully!")

    def is_chain_valid(self):

        for i in range(1, len(self.chain)):

            current = self.chain[i]
            previous = self.chain[i - 1]

            if current.hash != current.calculate_hash():
                return False

            if current.previous_hash != previous.hash:
                return False

        return True

    def save_chain(self):

        data = []

        for block in self.chain:

            data.append({
                "index": block.index,
                "timestamp": block.timestamp,
                "transactions": block.transactions,
                "previous_hash": block.previous_hash,
                "nonce": block.nonce
            })

        with open(self.file_name, "w") as f:
            json.dump(data, f, indent=4)

    def load_chain(self):

        with open(self.file_name, "r") as f:
            data = json.load(f)

        self.chain = []

        for block_data in data:

            block = Block(
                block_data["index"],
                block_data["timestamp"],
                block_data["transactions"],
                block_data["previous_hash"],
                block_data["nonce"]
            )

            self.chain.append(block)


# -----------------
# Demo
# -----------------

coin = Blockchain()

print("Blockchain Valid:", coin.is_chain_valid())

coin.mine_pending_transactions("Satoshi")

print("Satoshi Balance:", coin.get_balance("Satoshi"))

coin.add_transaction("Satoshi", "Alice", 20)

coin.mine_pending_transactions("Miner1")

print("Satoshi Balance:", coin.get_balance("Satoshi"))
print("Alice Balance:", coin.get_balance("Alice"))
print("Miner1 Balance:", coin.get_balance("Miner1"))

print("\nBlockchain Contents:")

for block in coin.chain:
    print("\n------------------")
    print("Block:", block.index)
    print("Hash:", block.hash)
    print("Previous Hash:", block.previous_hash)
    print("Transactions:", block.transactions)
