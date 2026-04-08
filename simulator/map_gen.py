"""
Forage & Dominion - Map Generator
Version: 1.1.0

Changes from v1.0.0:
- Resource cluster drift: slight position variation per match
"""
import random
import math
from typing import List, Tuple, Dict, Any, Optional
from simulator.entities import Map, Cell


PROTOCOL_VERSION = "1.1.0"


class MapGenerator:
    """Generates maps with rotational symmetry."""
    
    GRID_SIZE = 25
    MIN_SPAWN_DISTANCE = 8
    
    MAP_ARCHETYPES = {
        "open_field": {
            "wall_density": 0.05,
            "resource_clusters": 6,
            "cluster_size": 4,
        },
        "labyrinth": {
            "wall_density": 0.35,
            "resource_clusters": 12,
            "cluster_size": 1,
        },
        "crucible": {
            "wall_density": 0.10,
            "resource_clusters": 1,
            "cluster_size": 16,
            "central_node": True,
        },
    }
    
    def __init__(self, rng: random.Random):
        self.rng = rng
    
    def generate(self, archetype: str = None, num_players: int = 4,
                 match_rng: Optional[random.Random] = None) -> Tuple[Map, List[Tuple[int, int]]]:
        """
        Generate a map with the specified archetype.
        
        Args:
            archetype: "open_field" | "labyrinth" | "crucible"
            num_players: Number of players (2-4)
            match_rng: Optional RNG for seeded variation (resource cluster drift)
            
        Returns:
            Tuple of (Map, spawn_positions)
        """
        rng = match_rng or self.rng
        
        if archetype is None:
            archetype = rng.choice(list(self.MAP_ARCHETYPES.keys()))
        
        game_map = Map(rng)
        
        drift_x = rng.randint(-2, 2)
        drift_y = rng.randint(-2, 2)
        
        if archetype == "open_field":
            self._generate_open_field(game_map, drift_x, drift_y)
        elif archetype == "labyrinth":
            self._generate_labyrinth(game_map, drift_x, drift_y)
        elif archetype == "crucible":
            self._generate_crucible(game_map, drift_x, drift_y)
        
        spawn_positions = self._generate_spawns(game_map, num_players, rng)
        
        return game_map, spawn_positions
    
    def _generate_open_field(self, game_map: Map, drift_x: int, drift_y: int):
        """Generate open field map."""
        config = self.MAP_ARCHETYPES["open_field"]
        
        for y in range(self.GRID_SIZE):
            for x in range(self.GRID_SIZE):
                if self.rng.random() < config["wall_density"]:
                    game_map.grid[y][x].terrain = "wall"
        
        for _ in range(config["resource_clusters"]):
            cx = self.rng.randint(3, self.GRID_SIZE - 4) + drift_x
            cy = self.rng.randint(3, self.GRID_SIZE - 4) + drift_y
            cx = max(1, min(self.GRID_SIZE - 2, cx))
            cy = max(1, min(self.GRID_SIZE - 2, cy))
            for _ in range(config["cluster_size"]):
                dx = self.rng.randint(-1, 1)
                dy = self.rng.randint(-1, 1)
                gx = max(0, min(self.GRID_SIZE-1, cx + dx))
                gy = max(0, min(self.GRID_SIZE-1, cy + dy))
                game_map.add_resource(gx, gy)
    
    def _generate_labyrinth(self, game_map: Map, drift_x: int, drift_y: int):
        """Generate labyrinth map."""
        config = self.MAP_ARCHETYPES["labyrinth"]
        
        for y in range(self.GRID_SIZE):
            for x in range(self.GRID_SIZE):
                if self.rng.random() < config["wall_density"]:
                    game_map.grid[y][x].terrain = "wall"
        
        for _ in range(config["resource_clusters"]):
            x = self.rng.randint(0, self.GRID_SIZE - 1) + drift_x
            y = self.rng.randint(0, self.GRID_SIZE - 1) + drift_y
            x = max(0, min(self.GRID_SIZE - 1, x))
            y = max(0, min(self.GRID_SIZE - 1, y))
            game_map.add_resource(x, y)
    
    def _generate_crucible(self, game_map: Map, drift_x: int, drift_y: int):
        """Generate crucible map."""
        config = self.MAP_ARCHETYPES["crucible"]
        
        for y in range(self.GRID_SIZE):
            for x in range(self.GRID_SIZE):
                if self.rng.random() < config["wall_density"]:
                    game_map.grid[y][x].terrain = "wall"
        
        cx = self.GRID_SIZE // 2 + drift_x
        cy = self.GRID_SIZE // 2 + drift_y
        cx = max(2, min(self.GRID_SIZE - 3, cx))
        cy = max(2, min(self.GRID_SIZE - 3, cy))
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                game_map.add_resource(cx + dx, cy + dy, Map.RESOURCE_TILE_MAX)
    
    def _generate_spawns(self, game_map: Map, num_players: int, rng: random.Random) -> List[Tuple[int, int]]:
        """Generate rotationally symmetric spawn positions."""
        positions = []
        quadrant_size = self.GRID_SIZE // 2
        
        base_spawn = (
            rng.randint(2, quadrant_size - 2),
            rng.randint(2, quadrant_size - 2)
        )
        
        rotations = [
            (1, 1),
            (-1, 1),
            (1, -1),
            (-1, -1),
        ]
        
        for i in range(num_players):
            sx = base_spawn[0] * rotations[i][0]
            sy = base_spawn[1] * rotations[i][1]
            
            if sx < 0:
                sx = self.GRID_SIZE + sx
            if sy < 0:
                sy = self.GRID_SIZE + sy
            
            sx = max(0, min(self.GRID_SIZE - 1, sx))
            sy = max(0, min(self.GRID_SIZE - 1, sy))
            
            positions.append((sx, sy))
        
        return positions
    
    def get_archetypes(self) -> List[str]:
        """Get list of available archetypes."""
        return list(self.MAP_ARCHETYPES.keys())
