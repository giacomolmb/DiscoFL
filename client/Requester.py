import json
import math
from turtle import shape
import numpy as np
from web3 import Web3, HTTPProvider

class Requester:

    w3 = None
    truffle_file = json.load(open('./build/contracts/FLTask.json'))
    contract = None

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
            'gas': 2508712,
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

    def start_task(self):
        contract_instance = self.w3.eth.contract(abi=self.truffle_file['abi'], address=self.contract_address)

        tx = contract_instance.functions.startTask().buildTransaction({
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
        print("Task started successfully!")
    

    # calculate the top K of the round using the contribution scoring procedure from blockflow
    # inputs: score matrix dimension n x n where n = num_workers, number of workers
    # output: round top k with index of best performing workers
    def calc_overall_scores(self, score_matrix, num_workers):
        m = [] # median scores of each worker (m_k)
        m_scaled = [] # scaled median scores of each worker (m_k)
        t = np.full((num_workers, num_workers), -1.0) # evaluation quality scores
        t_scaled = np.full((num_workers, num_workers), -1.0) # transformed evaluation quality scores
        d = [] # least accurate evaluation each client performed
        overall_scores = [] # overall scores

        scores = np.array(score_matrix)

        #calculate median scores of each worker
        for i in range(num_workers):
            worker_scores = scores[:, i]
            scores_without_self = np.delete(worker_scores, i)
            m.append(np.median(scores_without_self))

        max_median = np.array(m).max() # maximum median score

        # scale median scores to ensure a maximum of 1.0
        for i in range(num_workers):
            m_scaled.append(m[i]/max_median)

        for i in range(num_workers):
            for j in range(num_workers):
                if i != j:
                    t[i, j] = abs(scores[i, j] - m[j]) # compute evaluation quality scores
                    t_scaled[i, j] = max(0, (0.5-t[i, j])/(0.5+t[i, j])) # transform evaluation quality scores
        
        for i in range(num_workers):
            quality_scores = t_scaled[i]
            quality_scores_without_self = np.delete(quality_scores, i)
            d.append(np.array(quality_scores_without_self).min()) # compute least accurate evaluation for each client

        max_d = np.array(d).max() # maximum value of least accurate evaluations used for scaling

        for i in range(num_workers):
            overall_scores.append(min(m_scaled[i], (d[i]/max_d))) # compute overall score as the minimum between m_scaled and d_scaled
        
        return overall_scores

        
        
