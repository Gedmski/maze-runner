"""
Parallel Maze Explorer module that implements distributed maze solving using MPI4Py.
"""

import time
from typing import Tuple, List, Dict, Any
from mpi4py import MPI
import json
import os
from .explorer import Explorer
from .explorer_astar import ExplorerAStar
from .maze import create_maze

class ParallelExplorer:
    def __init__(self, maze_type: str = "static", width: int = 30, height: int = 30):
        self.comm = MPI.COMM_WORLD
        self.rank = self.comm.Get_rank()
        self.size = self.comm.Get_size()
        self.maze_type = maze_type
        self.width = width
        self.height = height
        
        # Create the maze on all processes
        self.maze = create_maze(width, height, maze_type)
        
        # Initialize explorers
        self.explorers = {
            "original": Explorer(self.maze, visualize=False),
            "astar": ExplorerAStar(self.maze, visualize=False)
        }
        
        # Results storage
        self.results = {}
    
    def run_explorer(self, explorer_name: str) -> Dict[str, Any]:
        """Run a single explorer and return its results."""
        explorer = self.explorers[explorer_name]
        time_taken, moves = explorer.solve()
        
        return {
            "algorithm": explorer_name,
            "time_taken": time_taken,
            "moves": len(moves),
            "moves_per_second": len(moves) / time_taken if time_taken > 0 else 0,
            "path": moves
        }
    
    def run_parallel(self) -> Dict[str, Any]:
        """Run explorers in parallel across MPI processes."""
        # Each process runs a different explorer
        explorer_names = list(self.explorers.keys())
        explorer_name = explorer_names[self.rank % len(explorer_names)]
        
        # Run the explorer
        result = self.run_explorer(explorer_name)
        
        # Gather results from all processes
        all_results = self.comm.gather(result, root=0)
        
        # Process 0 analyzes and returns the results
        if self.rank == 0:
            return self.analyze_results(all_results)
        
        return None
    
    def analyze_results(self, all_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze and compare results from all explorers."""
        # Group results by algorithm
        algorithm_results = {}
        for result in all_results:
            algo = result["algorithm"]
            if algo not in algorithm_results:
                algorithm_results[algo] = []
            algorithm_results[algo].append(result)
        
        # Calculate statistics for each algorithm
        analysis = {
            "algorithms": {},
            "best_algorithm": None,
            "best_moves": float('inf'),
            "best_time": float('inf'),
            "best_moves_per_second": 0
        }
        
        for algo, results in algorithm_results.items():
            # Calculate averages
            avg_moves = sum(r["moves"] for r in results) / len(results)
            avg_time = sum(r["time_taken"] for r in results) / len(results)
            avg_moves_per_second = sum(r["moves_per_second"] for r in results) / len(results)
            
            # Find best result for this algorithm
            best_result = min(results, key=lambda r: r["moves"])
            
            analysis["algorithms"][algo] = {
                "average_moves": avg_moves,
                "average_time": avg_time,
                "average_moves_per_second": avg_moves_per_second,
                "best_moves": best_result["moves"],
                "best_time": best_result["time_taken"],
                "best_moves_per_second": best_result["moves_per_second"],
                "num_runs": len(results)
            }
            
            # Update overall best
            if best_result["moves"] < analysis["best_moves"]:
                analysis["best_moves"] = best_result["moves"]
                analysis["best_time"] = best_result["time_taken"]
                analysis["best_moves_per_second"] = best_result["moves_per_second"]
                analysis["best_algorithm"] = algo
        
        return analysis
    
    def print_results(self, analysis: Dict[str, Any]):
        """Print a summary of the results."""
        if analysis and self.rank == 0:  # Only print if we have results and we're the root process
            print("\n=== Parallel Maze Exploration Results ===")
            print(f"Total MPI processes: {self.size}")
            print(f"Maze type: {self.maze_type}")
            print(f"Maze dimensions: {self.width}x{self.height}")
            print("\nAlgorithm Statistics:")
            
            for algo, stats in analysis["algorithms"].items():
                print(f"\n{algo.upper()}:")
                print(f"  Number of runs: {stats['num_runs']}")
                print(f"  Average moves: {stats['average_moves']:.2f}")
                print(f"  Average time: {stats['average_time']:.2f} seconds")
                print(f"  Average moves/second: {stats['average_moves_per_second']:.2f}")
                print(f"  Best moves: {stats['best_moves']}")
                print(f"  Best time: {stats['best_time']:.2f} seconds")
                print(f"  Best moves/second: {stats['best_moves_per_second']:.2f}")
            
            print("\nOverall Best:")
            print(f"  Algorithm: {analysis['best_algorithm'].upper()}")
            print(f"  Moves: {analysis['best_moves']}")
            print(f"  Time: {analysis['best_time']:.2f} seconds")
            print(f"  Moves/second: {analysis['best_moves_per_second']:.2f}")
            print("=====================================\n") 