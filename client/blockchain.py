from Requester import Requester
from Worker import Worker
import os
from dotenv import load_dotenv

# Load private keys of blockchain addresses
load_dotenv()

REQUESTER_KEY = os.getenv("REQUESTER_KEY")
WORKER1_KEY = os.getenv("WORKER1_KEY")
WORKER2_KEY = os.getenv("WORKER2_KEY")
WORKER3_KEY = os.getenv("WORKER3_KEY")

requester = Requester(REQUESTER_KEY)
requester.deploy_contract()
requester.init_task(1000000000, "AAAAAAAAAA", 10)

worker1 = Worker(WORKER1_KEY)
worker1.join_task(requester.get_contract_address())
worker1.get_model_uri()

worker2 = Worker(WORKER2_KEY)
worker2.join_task(requester.get_contract_address())
worker2.get_model_uri()

worker3 = Worker(WORKER3_KEY)
worker3.join_task(requester.get_contract_address())
worker3.get_model_uri()

requester.start_task()
