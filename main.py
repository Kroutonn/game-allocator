# Internal Imports
from classes import allocatorUtil
from classes import event

# External Imports
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("--file", "-f", type=str, required=True, help="Name of input file")
    args = parser.parse_args()

    if args.file is not None:
        print(f"Loading in file: {args.file}")
        # First, an event needs to be set. This contains all the players, their preference scores and the game options
        event = event.Event()
        event.from_text_file(args.file)
    else:
        print("No file provided")

    solver = allocatorUtil.Solver(event)
    solver.check_all_combinations()