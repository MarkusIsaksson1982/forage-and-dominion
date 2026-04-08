"""
Forage & Dominion - TrueSkill Tracker
Version: 1.0.0
"""
import math
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass


PROTOCOL_VERSION = "1.0.0"


@dataclass
class Rating:
    """TrueSkill rating for an agent."""
    mu: float = 25.0
    sigma: float = 8.333
    beta: float = 4.166
    tau: float = 0.0833
    
    def __post_init__(self):
        self.games_played = 0
    
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
        ranks = [rank for _, rank in rankings]
        
        for label in players:
            rating = self.get_or_create_rating(label)
            self._update_rating(rating, players, ranks)
        
        self.history.append({
            "rankings": rankings,
            "ratings": {k: v.as_dict() for k, v in self.ratings.items()},
        })
        
        return self.ratings
    
    def _update_rating(self, rating: Rating, players: List[str], ranks: List[int]):
        """Update a single rating using TrueSkill formulas."""
        c = math.sqrt(rating.sigma**2 + rating.beta**2)
        
        v_func = self._v_function
        w_func = self._w_function
        
        players.sort(key=lambda p: ranks[players.index(p)])
        
        for i, player in enumerate(players):
            if player != rating:
                continue
                
            rank = ranks[i]
            n = len(players)
            
            sum_v = 0
            sum_w = 0
            
            for j, other in enumerate(players):
                if other == player:
                    continue
                    
                other_rank = ranks[j]
                t = (ranks[j] - rank) / c
                
                rank_diff = rank - other_rank
                if rank_diff < 0:
                    sum_v += v_func(t)
                elif rank_diff > 0:
                    sum_v -= v_func(-t)
                
                if other_rank < rank:
                    sum_w += w_func(t)
                elif other_rank > rank:
                    sum_w += w_func(-t)
            
            rating.mu += rating.sigma**2 / c * sum_v
            rating.sigma = math.sqrt(rating.sigma**2 * (1 - (rating.sigma**2 / c**2) * sum_w))
            rating.sigma = max(rating.sigma, rating.beta / 10)
            
            rating.games_played += 1
    
    def _v_function(self, t: float) -> float:
        """V function for TrueSkill."""
        pdf = (1 / math.sqrt(2 * math.pi)) * math.exp(-t**2 / 2)
        cdf = 0.5 * (1 + math.erf(t / math.sqrt(2)))
        
        if cdf < 1e-10:
            return -t
        return pdf / cdf
    
    def _w_function(self, t: float) -> float:
        """W function for TrueSkill."""
        pdf = (1 / math.sqrt(2 * math.pi)) * math.exp(-t**2 / 2)
        cdf = 0.5 * (1 + math.erf(t / math.sqrt(2)))
        
        if cdf < 1e-10 or (1 - cdf) < 1e-10:
            return 1
        
        v = self._v_function(t)
        return v * (v + t)
    
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
