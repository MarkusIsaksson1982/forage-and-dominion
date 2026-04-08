"""
Forage & Dominion - Gym Package
Version: 1.1.0
"""
from gym.agents.base_agent import BaseAgent
from gym.agents.random_agent import RandomMoveAgent
from gym.agents.greedy_forager import GreedyForagerAgent
from gym.agents.stationary_turret import StationaryTurretAgent
from gym.evaluator import Evaluator

__all__ = [
    "BaseAgent",
    "RandomMoveAgent", 
    "GreedyForagerAgent",
    "StationaryTurretAgent",
    "Evaluator",
    "PROTOCOL_VERSION",
]

PROTOCOL_VERSION = "1.1.0"
