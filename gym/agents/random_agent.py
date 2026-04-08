"""
Forage & Dominion - Random Agent
Version: 1.0.0
"""
import random
from typing import Dict, Any

from gym.agents.base_agent import BaseAgent


PROTOCOL_VERSION = "1.0.0"


class RandomMoveAgent(BaseAgent):
    """Baseline agent that moves randomly."""
    
    ACTION_TYPES = ["move", "collect", "idle"]
    DIRECTIONS = [[0, -1], [0, 1], [-1, 0], [1, 0]]
    
    def act(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """Choose a random valid action."""
        action_type = random.choice(self.ACTION_TYPES)
        
        if action_type == "move":
            direction = random.choice(self.DIRECTIONS)
            return {
                "type": "move",
                "params": {"dir": direction},
                "signal": 0,
            }
        
        if action_type == "collect":
            return {
                "type": "collect",
                "params": {},
                "signal": 0,
            }
        
        return {
            "type": "idle",
            "params": {},
            "signal": 0,
        }
