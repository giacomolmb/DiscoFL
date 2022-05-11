from Application import Application
import argparse
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Simulate the distributed execution locally')
    parser.add_argument('--num_workers', metavar='-N', type=int, help='number of workers to simulate the distributed environment')
    parser.add_argument('--index', metavar='-i', type=int, help='Index of current worker used for data splits')
    parser.add_argument('--fspath', metavar='-p', type=str, help='Path to the folder where the models are stored')
    args = parser.parse_args()
    Application(args.num_workers, args.index, args.fspath)