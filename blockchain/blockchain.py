import hashlib
import json
from time import time
from uuid import uuid4
from urllib.parse import urlparse
import requests
from flask import Flask, jsonify, request, send_from_directory

class Blockchain:
    """
    A simple blockchain implementation.

    Attributes:
        chain (list): A list of blocks.
        current_transactions (list): A list of current transactions.
        nodes (set): A set of network nodes.
    """

    def __init__(self):
        """
        Initializes the Blockchain with a genesis block.
        """
        self.chain = []
        self.current_transactions = []
        self.nodes = set()
        self.new_block(previous_hash='1', proof=100)

    def register_node(self, address):
        """
        Add a new node to the list of nodes.

        Args:
            address (str): Address of node. Eg. 'http://192.168.0.5:5000'
        """
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def new_block(self, proof, previous_hash=None):
        """
        Create a new block in the Blockchain.

        Args:
            proof (int): The proof given by the Proof of Work algorithm.
            previous_hash (str, optional): Hash of previous block.

        Returns:
            dict: New block.
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, owner, stamp, year, value):
        """
        Creates a new transaction to go into the next mined Block.

        Args:
            owner (str): Owner of the stamp.
            stamp (str): Stamp details.
            year (int): Year of the stamp.
            value (int): Value of the stamp.

        Returns:
            int: Index of the block that will hold this transaction.
        """
        self.current_transactions.append({
            'owner': owner,
            'stamp': stamp,
            'year': year,
            'value': value,
        })
        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        """
        Create a SHA-256 hash of a block.

        Args:
            block (dict): Block.

        Returns:
            str: Hash value.
        """
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        """
        Get the last block in the blockchain.

        Returns:
            dict: Last block.
        """
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        """
        Simple Proof of Work Algorithm:
        - Find a number p' such that hash(pp') contains leading 4 zeroes, where p is the previous p'
        - p is the previous proof, and p' is the new proof

        Args:
            last_proof (int): Previous proof.

        Returns:
            int: New proof.
        """
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        Validates the proof: Does hash(last_proof, proof) contain 4 leading zeroes?

        Args:
            last_proof (int): Previous proof.
            proof (int): Current proof.

        Returns:
            bool: True if correct, False if not.
        """
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def get_chain_length(self):
        """
        Get the length of the blockchain.

        Returns:
            int: Length of the blockchain.
        """
        return len(self.chain)

    def get_network_nodes(self):
        """
        Get the list of network nodes.

        Returns:
            list: List of network nodes.
        """
        return list(self.nodes)

app = Flask(__name__)

node_identifier = str(uuid4()).replace('-', '')

blockchain = Blockchain()

@app.route('/')
def root():
    """
    Root endpoint for serving the index.html file.

    Returns:
        str: index.html file.
    """
    return send_from_directory('.', 'index.html')

@app.route('/mine', methods=['GET'])
def mine():
    """
    Mine a new block.

    Returns:
        json: Mined block details.
    """
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    blockchain.new_transaction(
        owner="0",
        stamp="Genesis Stamp",
        year=0,
        value=0,
    )

    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    """
    Add a new transaction to the current transactions list.

    Returns:
        json: Message confirming the addition of transaction.
    """
    values = request.get_json()

    required = ['owner', 'stamp', 'year', 'value']
    if not all(k in values for k in required):
        return 'Missing values', 400

    index = blockchain.new_transaction(values['owner'], values['stamp'], values['year'], values['value'])

    response = {'message': f'Stamp Transaction will be added to Block {index}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    """
    Get the full blockchain.

    Returns:
        json: Full blockchain details.
    """
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    """
    Register new nodes.

    Returns:
        json: Message confirming the addition of nodes.
    """
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    """
    Resolve conflicts among nodes.

    Returns:
        json: Message indicating whether the chain was replaced or not.
    """
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200

@app.route('/chain/length', methods=['GET'])
def get_chain_length():
    """
    Get the length of the blockchain.

    Returns:
        json: Length of the blockchain.
    """
    chain_length = blockchain.get_chain_length()
    response = {'chain_length': chain_length}
    return jsonify(response), 200

@app.route('/nodes', methods=['GET'])
def get_network_nodes():
    """
    Get the list of network nodes.

    Returns:
        json: List of network nodes.
    """
    network_nodes = blockchain.get_network_nodes()
    response = {'network_nodes': network_nodes}
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)