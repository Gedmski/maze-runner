"""
Maze Explorer module that implements automated maze solving using A* pathfinding.
"""

import time
import pygame
from typing import Tuple, List, Optional, Set, Dict
from heapq import heappush, heappop
from .constants import BLUE, WHITE, CELL_SIZE, WINDOW_SIZE

class ExplorerAStar:
    def __init__(self, maze, visualize: bool = False):
        self.maze = maze
        self.x, self.y = maze.start_pos
        self.direction = (1, 0)  # Start facing right
        self.moves = []
        self.start_time = None
        self.end_time = None
        self.visualize = visualize
        if visualize:
            pygame.init()
            self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
            pygame.display.set_caption("Maze Explorer - A* Pathfinding")
            self.clock = pygame.time.Clock()

    def heuristic(self, pos: Tuple[int, int], goal: Tuple[int, int]) -> float:
        """Calculate Manhattan distance heuristic."""
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    def get_neighbors(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Get valid neighboring positions."""
        x, y = pos
        neighbors = []
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            new_x, new_y = x + dx, y + dy
            if (0 <= new_x < self.maze.width and 
                0 <= new_y < self.maze.height and 
                self.maze.grid[new_y][new_x] == 0):
                neighbors.append((new_x, new_y))
        return neighbors

    def draw_state(self, current_pos: Tuple[int, int], path: List[Tuple[int, int]]):
        """Draw the current state of the maze and explorer."""
        self.screen.fill(WHITE)
        
        # Draw maze
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                if self.maze.grid[y][x] == 1:
                    pygame.draw.rect(self.screen, (0, 0, 0),
                                   (x * CELL_SIZE, y * CELL_SIZE,
                                    CELL_SIZE, CELL_SIZE))
        
        # Draw path
        for x, y in path:
            pygame.draw.rect(self.screen, (200, 200, 255),
                           (x * CELL_SIZE, y * CELL_SIZE,
                            CELL_SIZE, CELL_SIZE))
        
        # Draw start and end points
        pygame.draw.rect(self.screen, (0, 255, 0),
                        (self.maze.start_pos[0] * CELL_SIZE,
                         self.maze.start_pos[1] * CELL_SIZE,
                         CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(self.screen, (255, 0, 0),
                        (self.maze.end_pos[0] * CELL_SIZE,
                         self.maze.end_pos[1] * CELL_SIZE,
                         CELL_SIZE, CELL_SIZE))
        
        # Draw current position
        pygame.draw.rect(self.screen, BLUE,
                        (current_pos[0] * CELL_SIZE,
                         current_pos[1] * CELL_SIZE,
                         CELL_SIZE, CELL_SIZE))
        
        pygame.display.flip()
        self.clock.tick(30)

    def print_statistics(self, time_taken: float):
        """Print detailed statistics about the exploration."""
        print("\n=== Maze Exploration Statistics (A*) ===")
        print(f"Total time taken: {time_taken:.2f} seconds")
        print(f"Total moves made: {len(self.moves)}")
        print(f"Average moves per second: {len(self.moves)/time_taken:.2f}")
        print("==================================\n")

    def solve(self) -> Tuple[float, List[Tuple[int, int]]]:
        """
        Solve the maze using A* pathfinding algorithm.
        Returns the time taken and the list of moves made.
        """
        self.start_time = time.time()
        
        # Initialize data structures for A*
        start = self.maze.start_pos
        goal = self.maze.end_pos
        open_set = [(0, start)]  # Priority queue of (f_score, position)
        came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}
        g_score: Dict[Tuple[int, int], float] = {start: 0}
        f_score: Dict[Tuple[int, int], float] = {start: self.heuristic(start, goal)}
        
        while open_set:
            current_f, current = heappop(open_set)
            
            if self.visualize:
                # Reconstruct path for visualization
                path = []
                pos = current
                while pos in came_from:
                    path.append(pos)
                    pos = came_from[pos]
                path.append(start)
                self.draw_state(current, path)
            
            if current == goal:
                # Reconstruct path
                path = []
                pos = current
                while pos in came_from:
                    path.append(pos)
                    pos = came_from[pos]
                path.append(start)
                path.reverse()
                self.moves = path
                break
            
            for neighbor in self.get_neighbors(current):
                tentative_g_score = g_score[current] + 1
                
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, goal)
                    heappush(open_set, (f_score[neighbor], neighbor))

        self.end_time = time.time()
        time_taken = self.end_time - self.start_time
        
        if self.visualize:
            # Show final path for a few seconds
            pygame.time.wait(2000)
            pygame.quit()
        
        # Print detailed statistics
        self.print_statistics(time_taken)
            
        return time_taken, self.moves 