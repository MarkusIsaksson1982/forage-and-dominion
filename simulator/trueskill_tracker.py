"""
Forage & Dominion - TrueSkill Tracker
Version: 1.0.0
"""
import math
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, field


PROTOCOL_VERSION = "1.0.0"


@dataclass
class Rating:
    """TrueSkill rating for an agent."""
    mu: float = 25.0
    sigma: float = 8.333
    beta: float = 4.166
    tau: float = 0.0833
    games_played: int = 0
    
    def as_dict(self) -> Dict[str, float]:
        return {
            "mu": self.mu,
            "sigma": self.sigma,
            "exposure": self.mu - 3 * self.sigma,
        }


class TrueSkillTracker:
    """Tracks TrueSkill ratings for tournament participants."""
    
    DEFAULT_PARAMS = {
        "mu": 25.0,
        "sigma": 8.333,
        "beta": 4.166,
        "tau": 0.0833,
        "draw_probability": 0.10,
    }
    
    def __init__(self, params: Dict[str, float] = None):
        self.params = {**self.DEFAULT_PARAMS, **(params or {})}
        self.ratings: Dict[str, Rating] = {}
        self.history: List[Dict[str, Any]] = []
    
    def get_or_create_rating(self, agent_id: str) -> Rating:
        """Get existing rating or create new one."""
        if agent_id not in self.ratings:
            self.ratings[agent_id] = Rating(
                mu=self.params["mu"],
                sigma=self.params["sigma"],
                beta=self.params["beta"],
                tau=self.params["tau"],
            )
        return self.ratings[agent_id]
    
    def update(self, rankings: List[Tuple[str, int]]) -> Dict[str, Rating]:
        """
        Update ratings based on match rankings.
        
        Args:
            rankings: List of (agent_id, rank) tuples, where rank 1 = winner
            
        Returns:
            Updated ratings dict
        """
        players = [label for label, _ in rankings]
        
        for label in players:
            rating = self.get_or_create_rating(label)
            rating.games_played += 1
        
        ranked = sorted(rankings, key=lambda x: x[1])
        
        for i, (player, rank) in enumerate(ranked):
            rating = self.ratings[player]
            
            better_count = sum(1 for _, r in rankings if r < rank)
            worse_count = sum(1 for _, r in rankings if r > rank)
            equal_count = sum(1 for _, r in rankings if r == rank) - 1
            
            total = len(players) - 1
            if total <= 0:
                continue
                
            win_rate = better_count / total
            
            sigma_factor = rating.sigma / (rating.sigma + self.params["beta"])
            
            if win_rate > 0.5:
                rating.mu += sigma_factor * (win_rate - 0.5) * 10
            else:
                rating.mu += sigma_factor * (win_rate - 0.5) * 10
            
            rating.sigma = max(rating.sigma * 0.98, self.params["beta"] / 10)
        
        self.history.append({
            "rankings": rankings,
            "ratings": {k: v.as_dict() for k, v in self.ratings.items()},
        })
        
        return self.ratings
    
    def get_rankings(self) -> List[Tuple[str, float]]:
        """Get current rankings sorted by exposure."""
        items = [(label, rating.as_dict()["exposure"]) for label, rating in self.ratings.items()]
        items.sort(key=lambda x: x[1], reverse=True)
        return items
    
    def get_leaderboard(self) -> List[Dict[str, Any]]:
        """Get full leaderboard with all metrics."""
        leaderboard = []
        for label, rating in self.ratings.items():
            d = rating.as_dict()
            leaderboard.append({
                "agent_id": label,
                "mu": d["mu"],
                "sigma": d["sigma"],
                "exposure": d["exposure"],
                "games_played": rating.games_played,
            })
        
        leaderboard.sort(key=lambda x: x["exposure"], reverse=True)
        return leaderboard
