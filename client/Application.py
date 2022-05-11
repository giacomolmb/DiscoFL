from BCCommunicator import BCCommunicator
from FSCommunicator import FSCommunicator
from Model import Model


class Application:
    def __init__(self, num_workers, current_index, fspath):
        self.num_workers = num_workers
        self.worker_idx = current_index
        self.bcc = BCCommunicator()
        self.fsc = FSCommunicator()
        self.model = Model(num_workers, current_index, fspath)
        
