## Setup
Create a virtual environment and install the requirements.txt.

## Running
The script is built to run on top of a Ganache testnet. It also requires Truffle to compile the smart contract.

Compile the smart contract running 
```
truffle compile
```

Create a `.env` file containing the private keys of requester and workers in the following format:
```
REQUESTER_KEY=0x...
WORKER1_KEY=0x...
WORKER2_KEY=0x...
WORKER3_KEY=0x...
...
```

Run the following python command
```
python main.py --num_workers 3 --num_rounds 10 --fspath fs-sim/
```

If you want to simulate a training session with evil workers, add the parameter `--num-evil` with the desired number of evil workers. 

