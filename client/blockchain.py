from Requester import Requester
from Worker import Worker

requester_key = input("Insert the private key of the requester: ")
requester = Requester("0x" + requester_key)
requester.deploy_contract()
requester.init_task(1000000000, "AAAAAAAAAA", 10)

worker1_key = input("Insert the private key of the worker 1: ")
worker1 = Worker("0x" + worker1_key)
worker1.join_task(requester.get_contract_address())
worker1.get_model_uri()

