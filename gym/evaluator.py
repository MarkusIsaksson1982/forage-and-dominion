"""
Forage & Dominion - Gym Evaluator
Version: 1.0.0
"""
import random
import json
from typing import List, Dict, Any, Optional
from simulator.engine import Engine
from simulator.entities import Commander


PROTOCOL_VERSION = "1.0.0"


class Evaluator:
    """Local evaluation runner for testing agents."""
    
    def __init__(self, seed: Optional[int] = None):
        self.rng = random.Random(seed)
        self.engine = Engine(self.rng)
    
    def evaluate_agent(self, agent, num_matches: int = 100,
                      opponents: List[Any] = None,
                      archetype: str = None) -> Dict[str, Any]:
        """
        Evaluate an agent against baseline opponents.
        
        Args:
            agent: Agent instance to evaluate
            opponents: List of opponent agents
            num_matches: Number of matches to run
            archetype: Optional map archetype
            
        Returns:
            Evaluation results with performance metrics
        """
        if opponents is None:
            from gym.agents.random_agent import RandomMoveAgent
            from gym.agents.greedy_forager import GreedyForagerAgent
            from gym.agents.stationary_turret import StationaryTurretAgent
            
            opponents = [
                RandomMoveAgent("opp_A", {}),
                GreedyForagerAgent("opp_B", {}),
                StationaryTurretAgent("opp_C", {}),
            ]
        
        wins = 0
        losses = 0
        ties = 0
        total_resources = 0
        total_survival = 0
        
        for match_id in range(num_matches):
            agents = [agent] + opponents
            arch = archetype if archetype else self.rng.choice(
                ["open_field", "labyrinth", "crucible"]
            )
            
            result = self.engine.run_match(
                agents=agents,
                match_id=match_id,
                archetype=arch
            )
            
            agent_rank = None
            for label, rank in result.rankings:
                if label == agent.player_id:
                    agent_rank = rank
                    break
            
            if agent_rank == 1:
                wins += 1
            elif agent_rank == len(agents):
                losses += 1
            else:
                ties += 1
            
            perf = result.performance_vectors.get(agent.player_id, {})
            total_resources += perf.get("resource_score", 0)
            total_survival += perf.get("survival_fraction", 0)
        
        return {
            "num_matches": num_matches,
            "wins": wins,
            "losses": losses,
            "ties": ties,
            "win_rate": wins / num_matches,
            "avg_resources": total_resources / num_matches,
            "avg_survival": total_survival / num_matches,
        }
    
    def run_baseline_test(self, agent) -> Dict[str, Any]:
        """Run standard baseline evaluation."""
        return self.evaluate_agent(agent, num_matches=100)
