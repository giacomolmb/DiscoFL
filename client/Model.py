import torch
import torchvision
import torch.nn.functional as F

class Model():
    '''
    Contains all machine learning functionality
    '''
    # static, might have to be calculated dynamically
    batch_size = 64
    epochs = 3

    def __init__(self, num_workers, idx, model, optimizer, device, topk, isEvil = False):
        self.num_workers = num_workers
        self.idx = idx
        self.model = model
        self.optimizer = optimizer
        self.DEVICE = device
        self.topk = topk
        self.isEvil = isEvil
        
        
        # this would be generic in a real application
        self.train_loader = torch.utils.data.DataLoader(
            torchvision.datasets.MNIST('./data', train=True, download=True,
                                       transform=torchvision.transforms.Compose([
                                           torchvision.transforms.ToTensor(),
                                           torchvision.transforms.Normalize(
                                               (0.1307,), (0.3081,))
                                       ])),
            batch_size=self.batch_size, shuffle=True)

        self.test_loader = torch.utils.data.DataLoader(
            torchvision.datasets.MNIST('./data', train=False, download=True,
                                       transform=torchvision.transforms.Compose([
                                           torchvision.transforms.ToTensor(),
                                           torchvision.transforms.Normalize(
                                               (0.1307,), (0.3081,))
                                       ])),
            batch_size=self.batch_size, shuffle=True)
        
        self.garbage = torch.rand((64,1,28,28))
        
        # find the datasets indices
        # also this would not be implemented like this in the real application
        # the users would use an 80/20 random split of their own dataset for training/validating
        self.num_train_batches = len(self.train_loader)//self.num_workers
        self.num_test_batches = len(self.test_loader)//self.num_workers 
        # start idx
        self.start_idx_train = self.num_test_batches* self.idx
        self.start_idx_test = self.num_test_batches * self.idx
        
        
    def average(self, state_dicts):
        # terrible way to do it
        final_dict = {}
        for key in state_dicts[0]:
            final_dict[key] = torch.clone(state_dicts[0][key])
            for i in state_dicts[1:]:
                final_dict[key] += torch.clone(i[key])
            final_dict[key]/=self.num_workers

        return final_dict
    
    
    def adapt_current_model(self, avg_state_dict):
        self.model.load_state_dict(avg_state_dict)


    def train(self):
        
        self.model.train()
        
        for epoch in range(self.epochs):
            for idx, (data, target) in enumerate(self.train_loader):
                if idx >= self.start_idx_train and idx < self.start_idx_train + self.num_train_batches:
                    self.optimizer.zero_grad()
                    if not self.isEvil:
                        output = self.model(data.to(self.DEVICE))
                    else:
                        output = self.model(self.garbage.to(self.DEVICE))
                        target = torch.randint(0, 8, (64,1)).reshape(64)
                    loss = F.nll_loss(output, target.to(self.DEVICE))
                    loss.backward()
                    self.optimizer.step()
            print('finished epoch {} of worker {}'.format(epoch, self.idx))
        return self.model.state_dict()

    def rank_models(self, sorted_models):
        return [self.num_workers - idx for idx in range(len(sorted_models))]
    
    def get_top_k(self, sorted_models):
        return [models[2] for models in sorted_models][-self.topk:]
    
    def test(self):
        self.model.eval()
        test_loss = 0
        correct = 0
        with torch.no_grad():
            for idx, (data, target) in enumerate(self.test_loader):
                if idx >= self.start_idx_test and idx < self.start_idx_test + self.num_test_batches:
                    output = self.model(data.to(self.DEVICE))
                    test_loss += F.nll_loss(output.to(self.DEVICE), target.to(self.DEVICE)).item()
                    pred = output.data.max(1, keepdim=True)[1]
                    correct += pred.eq(target.data.to(self.DEVICE).view_as(pred)).sum()
            test_loss /= (self.num_test_batches * self.batch_size)
        print('\nTest set: , Accuracy: {}/{} ({:.0f}%)\n'.format(
          correct, self.num_test_batches * self.batch_size,
          100. * correct / (self.num_test_batches * self.batch_size)))
        
        return correct / (self.num_test_batches*self.batch_size)
    
    def eval(self, model_state_dicts):
        res = []
        for idx, m in enumerate(model_state_dicts):
            self.model.load_state_dict(m)
            acc = self.test()
            res.append((acc,idx,m))
            
            
        sorted_models = sorted(res, key=lambda t: t[0])
        return self.rank_models(sorted_models),  self.get_top_k(sorted_models), res
            
            
            
            
        
        
        
