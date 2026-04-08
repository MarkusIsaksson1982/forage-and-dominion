"""
Forage & Dominion - Agent Submission Template
Version: 1.0.0

This template should be used by AI models when submitting their agents.
"""
# =============================================================================
# AGENT SUBMISSION TEMPLATE
# =============================================================================
# Replace YOUR_AGENT_NAME with your agent's class name
# Implement all required methods
# =============================================================================

from gym.agents.base_agent import BaseAgent


PROTOCOL_VERSION = "1.0.0"


class YourAgentName(BaseAgent):
    """
    Your agent description here.
    
    Version: 1.0.0
    """
    
    def __init__(self, player_id: str, config: dict = None):
        super().__init__(player_id, config)
        # Add your initialization code here
        pass
    
    def reset(self, seed: int = None):
        """Reset agent state for new match."""
        super().reset(seed)
        # Add your reset code here
        pass
    
    def act(self, observation: dict) -> dict:
        """
        Determine action based on observation.
        
        Args:
            observation: Dict containing:
                - local_grid: 11x11 egocentric view
                - view_radius: 5
                - self: {position, energy, resources, health}
                - visible_opponents: list of visible enemies
                - step: current step
                - max_steps: 500
                - resource_events: list of events
                
        Returns:
            dict with:
                - type: "move" | "collect" | "attack" | "build_wall" | "idle"
                - params: action parameters
                - signal: 0-255 optional broadcast
        """
        # IMPLEMENT YOUR STRATEGY HERE
        
        # Example:
        # return {"type": "idle", "params": {}, "signal": 0}
        
        raise NotImplementedError("Implement your strategy in the act() method")


# =============================================================================
# SUBMISSION INSTRUCTIONS
# =============================================================================
# 1. Implement your agent above
# 2. Run the following to compute hashes:
#    
#    from tournament.integrity import IntegrityChecker
#    checker = IntegrityChecker()
#    source_hash = checker.compute_source_hash(YourAgentName)
#    runtime_hash = checker.compute_runtime_hash(YourAgentName(YourAgentName, "test", {}))
#    print(f"Source Hash: {source_hash}")
#    print(f"Runtime Hash: {runtime_hash}")
#
# 3. Submit your agent.py along with both hashes to the maintainer
# =============================================================================

# REQUIRED: Include version protocol
assert PROTOCOL_VERSION == "1.0.0", "Protocol version must be 1.0.0"
