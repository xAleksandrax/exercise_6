# StampCoin Blockchain
StampCoin Blockchain is a simple blockchain project written in Python, utilizing the Flask library to build a basic API interface. The project allows for the creation of transactions related to stamp collecting and storing them in blocks to form a blockchain.

# Running
To run the project, follow these steps:

Run the blockchain server:
python blockchain.py
Open a web browser and navigate to http://localhost:5000/.

# API Interface
The project provides the following endpoints:

/mine - Generates a new block in the blockchain through the mining process.
/transactions/new - Adds a new transaction to the transaction pool.
/chain - Returns the entire blockchain in JSON format.
/nodes/register - Registers new nodes in the blockchain network.
/nodes/resolve - Resolves any conflicts between nodes in the blockchain network.

# Example Use Case
StampCoin Blockchain can be used to track the history of transactions and owners of postage stamps. It can also be expanded with additional features such as authentication, transaction validation, or creating custom nodes in the blockchain network.
