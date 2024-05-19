async function mine() {
    const response = await fetch('/mine');
    const data = await response.json();
    document.getElementById('message').innerHTML = data.message;
}

async function newTransaction() {
    const owner = document.getElementById('owner').value;
    const stamp = document.getElementById('stamp').value;
    const year = document.getElementById('year').value;
    const value = document.getElementById('value').value;
    
    const response = await fetch('/transactions/new', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ owner, stamp, year, value })
    });
    const data = await response.json();
    document.getElementById('transaction_message').innerHTML = data.message;
}

async function getChainLength() {
    const response = await fetch('/chain/length');
    const data = await response.json();
    document.getElementById('chain_length').innerHTML = `Chain Length: ${data.chain_length}`;
}

async function getNetworkNodes() {
    const response = await fetch('/nodes');
    const data = await response.json();
    document.getElementById('network_nodes').innerHTML = `Network Nodes: ${data.network_nodes.join(', ')}`;
}

document.getElementById('transactionForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    await newTransaction();
});
