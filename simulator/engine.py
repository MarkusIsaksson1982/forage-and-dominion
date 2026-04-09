"""
Forage & Dominion - Game Engine
Version: 1.2.0

Changes from v1.1.0:
- Hidden Variation Layer (HVL): stronger seeded perturbations (±15% damage, ±25% collect, ±2 regen)
- View radius reduced: 5 → 4 (11×11 → 9×9)
- Loot decay: continuous 5% per turn
- Probabilistic respawn: 0% → +15%/turn until 100%
"""
import hashlib
import json
import random
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field

from simulator.entities import Commander, Map, Cell
from simulator.map_gen import MapGenerator
from simulator.resolver import Resolver


PROTOCOL_VERSION = "1.2.0"


@dataclass
class HVLModifiers:
    """Hidden Variation Layer modifiers for a match."""
    base_damage_modifier: float = 1.0
    collect_yield_modifier: float = 1.0
    energy_regen_modifier: float = 1.0
    
    base_damage: float = 20.0
    collect_yield: int = 10
    energy_regen: int = 3
    
    def get_damage(self) -> float:
        return self.base_damage * self.base_damage_modifier
    
    def get_yield(self) -> int:
        return int(self.collect_yield * self.collect_yield_modifier)
    
    def get_regen(self) -> int:
        return int(self.energy_regen * self.energy_regen_modifier)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "base_damage": self.base_damage,
            "base_damage_modifier": self.base_damage_modifier,
            "collect_yield": self.collect_yield,
            "collect_yield_modifier": self.collect_yield_modifier,
            "energy_regen": self.energy_regen,
            "energy_regen_modifier": self.energy_regen_modifier,
        }


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
    hvl_modifiers: Dict[str, Any] = field(default_factory=dict)


class Engine:
    """Core game engine for Forage & Dominion."""
    
    GRID_SIZE = 25
    MAX_STEPS = 500
    VIEW_RADIUS = 4
    
    HVL_VARIANCE = {
        "damage": 0.15,
        "collect_yield": 0.25,
        "energy_regen": 2,
    }
    
    def __init__(self, rng: Optional[random.Random] = None):
        self.rng = rng or random.Random()
        self.map_generator = MapGenerator(self.rng)
        self.resolver = Resolver()
        self._current_map = None
        self._current_step = 0
    
    def _generate_hvl(self, match_rng: random.Random) -> HVLModifiers:
        """Generate HVL modifiers from seeded RNG."""
        mod = HVLModifiers()
        
        damage_variation = match_rng.uniform(-self.HVL_VARIANCE["damage"], self.HVL_VARIANCE["damage"])
        mod.base_damage_modifier = 1.0 + damage_variation
        
        yield_variation = match_rng.uniform(-self.HVL_VARIANCE["collect_yield"], self.HVL_VARIANCE["collect_yield"])
        mod.collect_yield_modifier = 1.0 + yield_variation
        
        regen_variation = match_rng.randint(-self.HVL_VARIANCE["energy_regen"], self.HVL_VARIANCE["energy_regen"])
        mod.energy_regen = 3 + regen_variation
        mod.energy_regen_modifier = 1.0
        
        return mod
    
    def _get_starting_energy(self, match_rng: random.Random, player_index: int) -> float:
        """Get asymmetric starting energy for a player."""
        variation = match_rng.randint(-5, 5)
        return 60.0 + variation
    
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
        
        hvl = self._generate_hvl(match_rng)
        
        game_map, spawn_positions = self.map_generator.generate(
            archetype=archetype,
            num_players=len(agents),
            match_rng=match_rng
        )
        
        self._current_map = game_map
        self._current_step = 0
        
        commanders = []
        for i, agent in enumerate(agents):
            label = f"opp_{chr(65 + i)}"
            if hasattr(agent, 'player_id'):
                label = agent.player_id
            
            starting_energy = self._get_starting_energy(match_rng, i)
            
            cmd = Commander(
                label=label,
                position=spawn_positions[i],
                health=Commander.MAX_HEALTH,
                energy=starting_energy,
                resources=0,
                base_damage=hvl.get_damage(),
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
            
            results = self.resolver.resolve(commanders, game_map, actions, hvl)
            
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
            game_map.decay_loot()
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
            hvl_modifiers=hvl.to_dict(),
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