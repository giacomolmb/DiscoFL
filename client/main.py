from Application import Application
import argparse
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Simulate the distributed execution locally')
    parser.add_argument('--num_workers', metavar='-M', type=int, help='number of workers to simulate the distributed environment')
    parser.add_argument('--num_rounds', metavar='-N', type=int, help='number of rounds that should be simulated')
    # not needed in simulation
    parser.add_argument('--index', metavar='-i', type=int, help='Index of current worker used for data splits')
    parser.add_argument('--fspath', metavar='-p', type=str, help='Path to the folder where the models are stored')
    parser.add_argument('--num_evil', metavar='-e', default=0, type=int, help='Number of evil workers you want')
    args = parser.parse_args()
    sim = Application(args.num_workers, args.num_rounds, args.fspath, args.num_evil)
    sim.run()
    