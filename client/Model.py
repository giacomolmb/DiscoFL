import torch
import torchvision


class Model():
    '''
    Contains all machine learning functionality
    '''
    # static, might have to be calculated dynamically
    batch_size = 64
    epochs = 5

    def __init__(self, num_workers, idx, model, optimizer):
        self.num_workers = num_workers
        self.idx = idx
        self.model = model
        self.optimizer = optimizer
        
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
        
        # find the datasets indices
        # also this would not be implemented like this in the real application
        # the users would use an 80/20 random split of their own dataset for training/validating
        self.start_idx_train = len(self.train_loader)/self.num_workers
        self.start_idx_test = len(self.test_loader)/self.num_workers

    def train(self):
        pass

    def eval(self):
        pass
