"""
Forage & Dominion - Base Agent Framework
Version: 1.0.0
"""
import hashlib
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseAgent(ABC):
    """
    Abstract base class for all agents in Forage & Dominion.
    
    Protocol Version: 1.0.0
    All agents must implement this interface to participate in tournaments.
    """
    
    PROTOCOL_VERSION = "1.0.0"
    
    def __init__(self, player_id: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the agent.
        
        Args:
            player_id: Unique identifier for this player (e.g., "agent_A")
            config: Optional configuration dictionary
        """
        self.player_id = player_id
        self.config = config or {}
        self._rng = None
        
    def reset(self, seed: Optional[int] = None):
        """
        Reset agent state for a new match.
        
        Args:
            seed: Random seed for deterministic behavior
        """
        import random
        self._rng = random.Random(seed)
        
    @abstractmethod
    def act(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determine action based on observation.
        
        Args:
            observation: Dict containing game state information
            
        Returns:
            Action dict with keys:
                - type: "move" | "collect" | "attack" | "build_wall" | "idle"
                - params: action-specific parameters
                - signal: optional 0-255 broadcast value
        """
        pass
    
    def get_hash(self) -> str:
        """
        Compute SHA256 hash of the agent's source code.
        
        Returns:
            Hex digest of SHA256 hash
        """
        import inspect
        source = inspect.getsource(self.__class__)
        return hashlib.sha256(source.encode()).hexdigest()
    
    def get_version(self) -> str:
        """
        Get the protocol version this agent implements.
        
        Returns:
            Protocol version string
        """
        return self.PROTOCOL_VERSION
