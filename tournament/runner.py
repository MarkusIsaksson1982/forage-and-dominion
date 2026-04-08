"""
Forage & Dominion - Tournament Runner
Version: 1.0.0
"""
import random
import hashlib
import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

from simulator.engine import Engine, MatchResult
from simulator.trueskill_tracker import TrueSkillTracker


PROTOCOL_VERSION = "1.0.0"


class TournamentRunner:
    """Orchestrates tournament execution."""
    
    def __init__(self, tournament_id: str, seed: Optional[int] = None):
        self.tournament_id = tournament_id
        self.seed = seed or int(time.time())
        self.rng = random.Random(self.seed)
        self.engine = Engine(self.rng)
        self.trueskill = TrueSkillTracker()
        
        self.results: List[MatchResult] = []
        self.hashes: Dict[str, str] = {}
    
    def register_agent(self, agent_id: str, source_hash: str, runtime_hash: str):
        """Register an agent with hashes."""
        self.hashes[agent_id] = {
            "source_hash": source_hash,
            "runtime_hash": runtime_hash,
        }
    
    def run_tournament(self, agents: List[Any], 
                     num_matches: int = 500,
                     archetypes: List[str] = None) -> Dict[str, Any]:
        """
        Run full tournament.
        
        Args:
            agents: List of agent instances
            num_matches: Number of matches to run
            archetypes: List of archetypes to sample from
            
        Returns:
            Tournament results dict
        """
        if archetypes is None:
            archetypes = ["open_field", "labyrinth", "crucible"]
        
        start_time = time.time()
        
        for match_id in range(num_matches):
            archetype = self.rng.choice(archetypes)
            
            shuffled_agents = agents.copy()
            self.rng.shuffle(shuffled_agents)
            
            result = self.engine.run_match(
                agents=shuffled_agents,
                match_id=match_id,
                tournament_id=self.tournament_id,
                archetype=archetype
            )
            
            self.results.append(result)
            
            if match_id % 100 == 0:
                rankings = [(label, rank) for label, rank in result.rankings]
                self.trueskill.update(rankings)
        
        elapsed_time = time.time() - start_time
        
        return self._compile_results(elapsed_time)
    
    def _compile_results(self, elapsed_time: float) -> Dict[str, Any]:
        """Compile final tournament results."""
        total_wins = {}
        total_matches = {}
        
        for result in self.results:
            for label, rank in result.rankings:
                if rank == 1:
                    total_wins[label] = total_wins.get(label, 0) + 1
                total_matches[label] = total_matches.get(label, 0) + 1
        
        win_rates = {
            label: total_wins.get(label, 0) / total_matches[label]
            for label in total_matches
        }
        
        stalemate_count = sum(1 for r in self.results if len(r.winners) > 1)
        stalemate_rate = stalemate_count / len(self.results) if self.results else 0
        
        evolution_triggered = self._check_evolution_triggers(win_rates, stalemate_rate)
        
        return {
            "tournament_id": self.tournament_id,
            "seed": self.seed,
            "num_matches": len(self.results),
            "elapsed_time_seconds": elapsed_time,
            "leaderboard": self.trueskill.get_leaderboard(),
            "win_rates": win_rates,
            "stalemate_rate": stalemate_rate,
            "evolution_triggered": evolution_triggered,
            "hashes": self.hashes,
            "match_seeds": [
                {"match_id": r.match_id, "seed": r.seed, "archetype": r.archetype}
                for r in self.results
            ],
        }
    
    def _check_evolution_triggers(self, win_rates: Dict[str, float],
                                  stalemate_rate: float) -> Optional[Dict[str, Any]]:
        """Check if any evolution triggers are met."""
        if len(self.results) < 500:
            return None
        
        for label, rate in win_rates.items():
            if rate > 0.75:
                return {
                    "trigger": "dominance",
                    "agent": label,
                    "win_rate": rate,
                }
        
        if stalemate_rate > 0.40:
            return {
                "trigger": "stalemate",
                "stalemate_rate": stalemate_rate,
            }
        
        return None
