import json
from web3 import Web3, HTTPProvider

class Worker:
    account = None
    key = ""
    w3 = None
    truffle_file = json.load(open('./build/contracts/FLTask.json'))
    contract = None
    contract_instance = None

    def __init__(self, key):
        self.key = key
        # init web3.py instance
        self.w3 = Web3(HTTPProvider("http://localhost:7545"))
        if(self.w3.isConnected()):
            print("Worker initialization: connected to blockchain")

        self.account = self.w3.eth.account.privateKeyToAccount(key)
        self.contract = self.w3.eth.contract(bytecode=self.truffle_file['bytecode'], abi=self.truffle_file['abi'])

    def join_task(self, contract_address):
        self.contract_address = contract_address
        self.contract_instance = self.w3.eth.contract(abi=self.truffle_file['abi'], address=contract_address)

        tx = self.contract_instance.functions.joinTask().buildTransaction({
            "gasPrice": self.w3.eth.gas_price, 
            "chainId": 1337, 
            "from": self.account.address, 
            'nonce': self.w3.eth.getTransactionCount(self.account.address)
        })
        #Get tx receipt to get contract address
        signed_tx = self.w3.eth.account.signTransaction(tx, self.key)
        tx_hash = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        tx_receipt = self.w3.eth.getTransactionReceipt(tx_hash)
        print(tx_receipt)
        print("Worker " + self.account.address + " has joined the task")

    def get_model_uri(self):
        print('SC Response - Model URI: {}'.format(self.contract_instance.functions.getModelURI().call()))

    def get_round_number(self):
        print('SC Response - Round number: {}'.format(self.contract_instance.functions.getRound().call()))