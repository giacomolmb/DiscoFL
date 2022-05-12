

import torch.optim as optim
from BCCommunicator import BCCommunicator
from FSCommunicator import FSCommunicator
from Model import Model


# this simulates one worker. Usually each device has one of these

class Worker:
    
    def __init__(self, fspath, device, num_workers, idx,topk):
        self.bcc = BCCommunicator()
        self.fsc = FSCommunicator(fspath, device)
        model, opt = self.fsc.fetch_initial_model()
        
        # This is incredibly hacky and should definitely not be done like this
        # we use pythons reflection ability to create the correct optimizer
        # it is not clear if that works for a general optimizer or only for opt.SGD
        class_ = getattr(optim, opt['name'])
        copy = dict(opt['state_dict']['param_groups'][0])
        try:
            del copy['params']
        except:
            pass
        opt = class_(model.parameters(), **(copy))
        self.model = Model(num_workers, idx, model, opt, device, topk)
        self.idx = idx
        self.num_workers = num_workers
        
        
    def train(self, round):
        # train
        cur_state_dict = self.model.train()
        # push to file system
        self.fsc.push_model(cur_state_dict, self.idx, round)    
    
    def evaluate(self, round):
        # retrieve all models of the other workers
        state_dicts = self.fsc.fetch_evaluation_models(self.idx, round, self.num_workers)
        
        ranks, topk_dicts = self.model.eval(state_dicts)
        
        # add our own model for the averaging
        topk_dicts.append(self.model.model.state_dict())
        
        # @TODO add blockchain functionality with sending the ranks to BC here
        
        return self.model.average(topk_dicts)
        
    
    
    def update_model(self, avg_dicts):
        # here we update the model with the averaged dicts
        self.model.adapt_current_model(avg_dicts)

        
        
        