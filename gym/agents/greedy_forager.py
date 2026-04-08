"""
Forage & Dominion - Greedy Forager Agent
Version: 1.0.0
"""
import random
from typing import Dict, Any, List, Tuple

from gym.agents.base_agent import BaseAgent


PROTOCOL_VERSION = "1.0.0"


class GreedyForagerAgent(BaseAgent):
    """Baseline agent that prioritizes collecting resources."""
    
    DIRECTIONS = [[0, -1], [0, 1], [-1, 0], [1, 0]]
    
    def act(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """Choose action prioritizing resource collection."""
        local_grid = observation.get("local_grid", [])
        self_state = observation.get("self", {})
        
        center = len(local_grid) // 2
        current_cell = local_grid[center][center]
        
        if current_cell.get("resource", 0) > 0:
            return {
                "type": "collect",
                "params": {},
                "signal": 0,
            }
        
        if current_cell.get("loot", 0) > 0:
            return {
                "type": "collect",
                "params": {},
                "signal": 0,
            }
        
        resources = self._find_nearest_resources(local_grid, center)
        
        if resources:
            direction = self._direction_to(center, center, resources[0], resources[1])
            return {
                "type": "move",
                "params": {"dir": direction},
                "signal": 0,
            }
        
        direction = random.choice(self.DIRECTIONS)
        return {
            "type": "move",
            "params": {"dir": direction},
            "signal": 0,
        }
    
    def _find_nearest_resources(self, grid: List[List], 
                               cx: int) -> Tuple[int, int]:
        """Find nearest resource cell."""
        min_dist = float('inf')
        nearest = None
        
        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                if cell.get("resource", 0) > 0 or cell.get("loot", 0) > 0:
                    dist = abs(x - cx) + abs(y - cx)
                    if dist < min_dist:
                        min_dist = dist
                        nearest = (x, y)
        
        return nearest if nearest else (cx, cx)
    
    def _direction_to(self, fx: int, fy: int, tx: int, ty: int) -> List[int]:
        """Get direction from from to to."""
        dx = tx - fx
        dy = ty - fy
        
        if abs(dx) >= abs(dy):
            return [1 if dx > 0 else -1, 0]
        else:
            return [0, 1 if dy > 0 else -1]
