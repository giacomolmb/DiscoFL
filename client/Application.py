from BCCommunicator import BCCommunicator
from FSCommunicator import FSCommunicator
from Model import Model
import torch
import os
from Requester import Requester
from Worker import Worker
from dotenv import load_dotenv

# Main class to simulate the distributed application
class Application:
    
    def __init__(self, num_workers, num_rounds, fspath, num_evil=0):
        self.num_workers = num_workers
        self.num_rounds = num_rounds
        self.DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.fspath = fspath
        self.workers = []
        self.topk = num_workers
        self.worker_dict = {}
        self.num_evil = num_evil
        
        
    def run(self):
        load_dotenv()
        self.requester = Requester(os.getenv('REQUESTER_KEY'))
        self.requester.deploy_contract()
        self.requester.init_task(10000000000000000000, self.fspath, self.num_rounds)
        print("Task initialized")

        # in the beginning, all have the same model
        # the optimizer stays the same over all round
        # initialize all workers sequentially
        # in a real application, each device would run one worker class
        for i in range(self.num_workers):
            self.workers.append(Worker(self.fspath, self.DEVICE, self.num_workers, i, 3, os.getenv('WORKER' + str(i+1) + '_KEY'), i < self.num_evil))
            self.worker_dict[i] = self.workers[i].account.address
            self.workers[i].join_task(self.requester.get_contract_address())
            print("Worker " + self.worker_dict[i] + " has joined the task")

        self.requester.start_task()
        print("Task started!")
        print("Number of workers joining the task: " + str(self.requester.num_workers))

        for round in range(self.num_rounds):
            print('Starting round {}'.format(round))
            for idx, worker in enumerate(self.workers):
                print('Worker {} starts to train'.format(idx))
                worker.train(round)
            
            # starting eval phase
            for idx,worker in enumerate(self.workers):
                avg_dicts, topK_dicts, unsorted_scores = worker.evaluate(round)
                unsorted_scores = [score[0].cpu().item() for score in unsorted_scores]
                unsorted_scores.insert(idx, -1)
                unsorted_scores = (idx, unsorted_scores)
                self.requester.push_scores(unsorted_scores)
                worker.update_model(avg_dicts)
            
            overall_scores = self.requester.calc_overall_scores(self.requester.get_score_matrix(), self.num_workers)
            round_top_k = self.requester.compute_top_k(list(self.worker_dict.values()), overall_scores)
            self.requester.submit_top_k(round_top_k)
            self.requester.distribute_rewards()
            print("Distributed rewards. Next round starting soon...")
            self.requester.next_round()
                                
        
        
             
