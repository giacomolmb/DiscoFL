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

worker1 = Worker("aaa","cpu",0,0,0,WORKER1_KEY)
worker1.join_task(requester.get_contract_address())
worker1.get_model_uri()

worker2 = Worker("aaa","cpu",0,0,0,WORKER2_KEY)
worker2.join_task(requester.get_contract_address())
worker2.get_model_uri()

worker3 = Worker("aaa","cpu",0,0,0,WORKER3_KEY)
worker3.join_task(requester.get_contract_address())
worker3.get_model_uri()

requester.start_task()
requester.get_num_workers()

round_top_k = ['0x449b5016E2b6155e69f514D6878eb73740d13751', '0x1677D1b1463733D6Dc14996413402B8ac1e64E73', '0x5678AE665f764B523091d2F9B048eeBCa39d6f1d']
requester.submit_top_k(round_top_k)