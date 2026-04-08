"""
Forage & Dominion - Stationary Turret Agent
Version: 1.0.0
"""
import random
from typing import Dict, Any

from gym.agents.base_agent import BaseAgent


PROTOCOL_VERSION = "1.0.0"


class StationaryTurretAgent(BaseAgent):
    """Baseline agent that builds walls for defense and attacks when threatened."""
    
    DIRECTIONS = [[0, -1], [0, 1], [-1, 0], [1, 0]]
    
    def act(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """Build defensive walls and attack nearby enemies."""
        self_state = observation.get("self", {})
        visible_opponents = observation.get("visible_opponents", [])
        
        if visible_opponents:
            targets = [opp["label"] for opp in visible_opponents]
            target = random.choice(targets)
            return {
                "type": "attack",
                "params": {"target_label": target},
                "signal": 0,
            }
        
        local_grid = observation.get("local_grid", [])
        center = len(local_grid) // 2
        
        has_resource = local_grid[center][center].get("resource", 0) > 0
        if has_resource:
            return {
                "type": "collect",
                "params": {},
                "signal": 0,
            }
        
        energy = self_state.get("energy", 0)
        if energy >= 50:
            direction = random.choice(self.DIRECTIONS)
            return {
                "type": "build_wall",
                "params": {"dir": direction},
                "signal": 0,
            }
        
        return {
            "type": "idle",
            "params": {},
            "signal": 0,
        }
