import json
from web3 import Web3, HTTPProvider

class Requester:
    account = None
    key = ""
    w3 = None
    truffle_file = json.load(open('./build/contracts/FLTask.json'))
    contract = None
    contract_address = None

    def __init__(self, key):
        self.key = key
        # init web3.py instance
        self.w3 = Web3(HTTPProvider("http://localhost:7545"))
        if(self.w3.isConnected()):
            print("Requester initialization: connected to blockchain")

        self.account = self.w3.eth.account.privateKeyToAccount(key)
        self.contract = self.w3.eth.contract(bytecode=self.truffle_file['bytecode'], abi=self.truffle_file['abi'])

    def deploy_contract(self):
        print(self.account.address)

        construct_txn = self.contract.constructor().buildTransaction({
            'from': self.account.address,
            'nonce': self.w3.eth.getTransactionCount(self.account.address),
            'gas': 2008712,
            'gasPrice': self.w3.toWei('21', 'gwei')
        })

        signed = self.account.signTransaction(construct_txn)

        tx_hash=self.w3.eth.sendRawTransaction(signed.rawTransaction)
        print(tx_hash.hex())
        tx_receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)
        self.contract_address = tx_receipt['contractAddress']
        print("Contract Deployed At:", self.contract_address)

    def get_contract_address(self):
        return self.contract_address

    def init_task(self, deposit, model_uri, num_rounds):
        contract_instance = self.w3.eth.contract(abi=self.truffle_file['abi'], address=self.contract_address)

        tx = contract_instance.functions.initializeTask(model_uri, num_rounds).buildTransaction({
            "gasPrice": self.w3.eth.gas_price, 
            "chainId": 1337, 
            "from": self.account.address, 
            "value": deposit,
            'nonce': self.w3.eth.getTransactionCount(self.account.address)
        })
        #Get tx receipt to get contract address
        signed_tx = self.w3.eth.account.signTransaction(tx, self.key)
        tx_hash = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        tx_receipt = self.w3.eth.getTransactionReceipt(tx_hash)
        print(tx_receipt)
        print("Task initialized successfully!")