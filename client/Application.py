from BCCommunicator import BCCommunicator
from FSCommunicator import FSCommunicator
from Model import Model
import torch

from Worker import Worker


# Main class to simulate the distributed application
class Application:
    
    def __init__(self, num_workers, num_rounds, fspath):
        self.num_workers = num_workers
        self.num_rounds = num_rounds
        self.DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.fspath = fspath
        self.workers = []
        self.topk = 3
        
        
    def run(self):
        
        # in the beginning, all have the same model
        # the optimizer stays the same over all round
        # initialize all workers sequentially
        # in a real application, each device would run one worker class
        for i in range(self.num_workers):
            self.workers.append(Worker(self.fspath, self.DEVICE, self.num_workers, i, 3))
            
        
    
        for round in range(self.num_rounds):
            print('Starting round {}'.format(round))
            for idx, worker in enumerate(self.workers):
                print('Worker {} starts to train'.format(idx))
                worker.train(round)
            
            # starting eval phase
            for worker in self.workers:
                avg_dicts = worker.evaluate(round)
                worker.update_model(avg_dicts)
                
        
        
             
