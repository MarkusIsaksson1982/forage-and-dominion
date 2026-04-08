"""
Forage & Dominion - Game Engine
Version: 1.0.0
"""
import hashlib
import json
import random
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field

from simulator.entities import Commander, Map, Cell
from simulator.map_gen import MapGenerator
from simulator.resolver import Resolver


PROTOCOL_VERSION = "1.0.0"


@dataclass
class MatchResult:
    """Result of a single match."""
    match_id: int
    seed: int
    archetype: str
    winners: List[str]
    rankings: List[Tuple[str, int]]
    commanders: List[Dict[str, Any]]
    performance_vectors: Dict[str, Dict[str, float]] = field(default_factory=dict)
    events: List[Dict[str, Any]] = field(default_factory=list)


class Engine:
    """Core game engine for Forage & Dominion."""
    
    GRID_SIZE = 25
    MAX_STEPS = 500
    VIEW_RADIUS = 5
    
    def __init__(self, rng: Optional[random.Random] = None):
        self.rng = rng or random.Random()
        self.map_generator = MapGenerator(self.rng)
        self.resolver = Resolver()
        self._current_map = None
        self._current_step = 0
    
    def run_match(self, agents: List[Any], match_id: int = 0,
                  tournament_id: str = "default",
                  archetype: str = None) -> MatchResult:
        """
        Run a single match between agents.
        
        Args:
            agents: List of agent instances implementing BaseAgent
            match_id: Unique match identifier
            tournament_id: Tournament identifier for seed generation
            archetype: Map archetype to use
            
        Returns:
            MatchResult with rankings and performance data
        """
        seed = int(hashlib.sha256(f"{tournament_id}_{match_id}".encode()).hexdigest()[:8], 16)
        match_rng = random.Random(seed)
        
        game_map, spawn_positions = self.map_generator.generate(
            archetype=archetype,
            num_players=len(agents)
        )
        
        self._current_map = game_map
        self._current_step = 0
        
        commanders = []
        for i, agent in enumerate(agents):
            label = f"opp_{chr(65 + i)}"
            if hasattr(agent, 'player_id'):
                label = agent.player_id
            
            cmd = Commander(
                label=label,
                position=spawn_positions[i],
                health=Commander.MAX_HEALTH,
                energy=Commander.STARTING_ENERGY,
                resources=0,
            )
            commanders.append(cmd)
            
            agent.reset(seed=match_rng.randint(0, 2**31 - 1))
        
        step = 0
        events = []
        
        while step < self.MAX_STEPS:
            alive_commanders = [c for c in commanders if c.alive]
            if len(alive_commanders) <= 1:
                break
            
            actions = self._get_actions(commanders, agents, game_map)
            
            results = self.resolver.resolve(commanders, game_map, actions)
            
            for cmd in commanders:
                cmd.decrement_stun()
                if cmd.energy <= 0:
                    cmd.apply_stun()
            
            for result in results:
                if result.damage_dealt > 0:
                    events.append({
                        "step": step,
                        "type": "combat",
                        "attacker": result.commander_label,
                        "damage": result.damage_dealt,
                    })
                
                if result.resources_gained > 0:
                    events.append({
                        "step": step,
                        "type": "collect",
                        "commander": result.commander_label,
                        "amount": result.resources_gained,
                    })
            
            game_map.respawn_resources()
            self._current_step = step
            step += 1
        
        rankings = self._compute_rankings(commanders)
        
        winners = [label for label, rank in rankings if rank == 1]
        
        performance_vectors = self._compute_performance_vectors(commanders, step)
        
        return MatchResult(
            match_id=match_id,
            seed=seed,
            archetype=archetype or "random",
            winners=winners,
            rankings=rankings,
            commanders=[c.to_dict() for c in commanders],
            performance_vectors=performance_vectors,
            events=events,
        )
    
    def _get_actions(self, commanders: List[Commander], 
                     agents: List[Any], game_map: Map) -> Dict[str, Dict[str, Any]]:
        """Get actions from all agents."""
        actions = {}
        
        for cmd, agent in zip(commanders, agents):
            if not cmd.alive:
                actions[cmd.label] = {"type": "idle", "params": {}}
                continue
            
            observation = self._build_observation(cmd, commanders, game_map)
            
            try:
                action = agent.act(observation)
                if not isinstance(action, dict):
                    action = {"type": "idle", "params": {}}
            except Exception:
                action = {"type": "idle", "params": {}}
            
            actions[cmd.label] = action
            
            cmd.last_signal = action.get("signal", 0)
        
        return actions
    
    def _build_observation(self, commander: Commander, 
                          all_commanders: List[Commander],
                          game_map: Map) -> Dict[str, Any]:
        """Build observation dict for a commander."""
        local_grid = game_map.get_egocentric_view(commander.position, self.VIEW_RADIUS)
        
        grid_dict = []
        for row in local_grid:
            grid_dict.append([cell.to_dict() for cell in row])
        
        visible_opponents = []
        for other in all_commanders:
            if other.label == commander.label or not other.alive:
                continue
            
            dist = (abs(commander.position[0] - other.position[0]) + 
                   abs(commander.position[1] - other.position[1]))
            
            if dist > self.VIEW_RADIUS:
                continue
            
            has_los = game_map.has_line_of_sight(commander.position, other.position)
            if not has_los:
                continue
            
            visible_opponents.append({
                "label": other.label,
                "position": list(other.position),
                "health_bracket": other.get_health_bracket(),
                "signal": other.last_signal,
            })
        
        return {
            "local_grid": grid_dict,
            "view_radius": self.VIEW_RADIUS,
            "self": commander.to_dict(),
            "visible_opponents": visible_opponents,
            "step": self._current_step,
            "max_steps": self.MAX_STEPS,
            "resource_events": [],
        }
    
    def _compute_rankings(self, commanders: List[Commander]) -> List[Tuple[str, int]]:
        """Compute final rankings."""
        alive = [c for c in commanders if c.alive]
        if not alive:
            return [(c.label, len(commanders)) for c in commanders]
        
        alive.sort(key=lambda c: (-c.resources, -c.health))
        
        rankings = []
        for rank, cmd in enumerate(alive, 1):
            rankings.append((cmd.label, rank))
        
        dead = [c for c in commanders if not c.alive]
        for cmd in dead:
            rankings.append((cmd.label, len(commanders)))
        
        return rankings
    
    def _compute_performance_vectors(self, commanders: List[Commander],
                                     final_step: int) -> Dict[str, Dict[str, float]]:
        """Compute performance vector for each commander."""
        vectors = {}
        
        max_resources = max(c.resources for c in commanders) or 1
        
        for cmd in commanders:
            vectors[cmd.label] = {
                "resource_score": cmd.resources / max_resources,
                "survival_fraction": final_step / self.MAX_STEPS,
                "combat_efficiency": 0.0,
                "collection_rate": 0.0,
            }
        
        return vectors
