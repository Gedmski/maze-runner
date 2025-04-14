"""
Main entry point for the maze runner game.
"""

import argparse
from src.game import run_game
from src.explorer import Explorer
from src.explorer_astar import ExplorerAStar
from src.parallel_explorer import ParallelExplorer
from mpi4py import MPI


def main():
    parser = argparse.ArgumentParser(description="Maze Runner Game")
    parser.add_argument("--type", choices=["random", "static"], default="random",
                        help="Type of maze to generate (random or static)")
    parser.add_argument("--width", type=int, default=30,
                        help="Width of the maze (default: 30, ignored for static mazes)")
    parser.add_argument("--height", type=int, default=30,
                        help="Height of the maze (default: 30, ignored for static mazes)")
    parser.add_argument("--auto", action="store_true",
                        help="Run automated maze exploration")
    parser.add_argument("--visualize", action="store_true",
                        help="Visualize the automated exploration in real-time")
    parser.add_argument("--algorithm", choices=["original", "astar"], default="original",
                        help="Algorithm to use for automated exploration (original or astar)")
    parser.add_argument("--parallel", action="store_true",
                        help="Run parallel exploration using MPI")
    
    args = parser.parse_args()
    
    if args.parallel:
        # Run parallel exploration using MPI
        parallel_explorer = ParallelExplorer(
            maze_type=args.type,
            width=args.width,
            height=args.height
        )
        results = parallel_explorer.run_parallel()
        parallel_explorer.print_results(results)
    elif args.auto:
        # Create maze and run automated exploration
        from src.maze import create_maze
        maze = create_maze(args.width, args.height, args.type)
        
        # Choose explorer based on algorithm argument
        if args.algorithm == "astar":
            explorer = ExplorerAStar(maze, visualize=args.visualize)
        else:
            explorer = Explorer(maze, visualize=args.visualize)
            
        time_taken, moves = explorer.solve()
        print(f"Maze solved in {time_taken:.2f} seconds")
        print(f"Number of moves: {len(moves)}")
        if args.type == "static":
            print("Note: Width and height arguments were ignored for the static maze")
    else:
        # Run the interactive game
        run_game(maze_type=args.type, width=args.width, height=args.height)


if __name__ == "__main__":
    main()