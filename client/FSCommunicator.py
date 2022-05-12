import torch
import sys

class FSCommunicator:


    def __init__(self, fspath, device):
        """
        Initializes the connection and pulls the initial model together with the optimizer that is used
        """
        self.path = fspath
        self.DEVICE = device
        
    def fetch_initial_model(self):
        return torch.jit.load(self.path + 'model.pt', map_location=self.DEVICE), torch.load(self.path + 'optimizer.pt', map_location=self.DEVICE)

    
    def fetch_evaluation_models(self, worker_index, round, num_workers):
        state_dicts = []
        for i in range(num_workers):
            if i != worker_index: state_dicts.append(torch.load(self.path + 'model_round_{}_index_{}.pt'.format(round,i)))
        return state_dicts
    

    def push_model(self, state_dict, worker_index, round):
        torch.save(state_dict, self.path + 'model_round_{}_index_{}.pt'.format(round, worker_index))

