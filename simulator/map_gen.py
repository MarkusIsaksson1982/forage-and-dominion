"""
Forage & Dominion - Map Generator
Version: 1.0.0
"""
import random
import math
from typing import List, Tuple, Dict, Any
from simulator.entities import Map, Cell


PROTOCOL_VERSION = "1.0.0"


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
    
    def generate(self, archetype: str = None, num_players: int = 4) -> Tuple[Map, List[Tuple[int, int]]]:
        """
        Generate a map with the specified archetype.
        
        Args:
            archetype: "open_field" | "labyrinth" | "crucible"
            num_players: Number of players (2-4)
            
        Returns:
            Tuple of (Map, spawn_positions)
        """
        if archetype is None:
            archetype = self.rng.choice(list(self.MAP_ARCHETYPES.keys()))
        
        game_map = Map(self.rng)
        
        if archetype == "open_field":
            self._generate_open_field(game_map)
        elif archetype == "labyrinth":
            self._generate_labyrinth(game_map)
        elif archetype == "crucible":
            self._generate_crucible(game_map)
        
        spawn_positions = self._generate_spawns(game_map, num_players)
        
        return game_map, spawn_positions
    
    def _generate_open_field(self, game_map: Map):
        """Generate open field map."""
        config = self.MAP_ARCHETYPES["open_field"]
        
        for y in range(self.GRID_SIZE):
            for x in range(self.GRID_SIZE):
                if self.rng.random() < config["wall_density"]:
                    game_map.grid[y][x].terrain = "wall"
        
        for _ in range(config["resource_clusters"]):
            cx = self.rng.randint(3, self.GRID_SIZE - 4)
            cy = self.rng.randint(3, self.GRID_SIZE - 4)
            for _ in range(config["cluster_size"]):
                dx = self.rng.randint(-1, 1)
                dy = self.rng.randint(-1, 1)
                game_map.add_resource(cx + dx, cy + dy)
    
    def _generate_labyrinth(self, game_map: Map):
        """Generate labyrinth map."""
        config = self.MAP_ARCHETYPES["labyrinth"]
        
        for y in range(self.GRID_SIZE):
            for x in range(self.GRID_SIZE):
                if self.rng.random() < config["wall_density"]:
                    game_map.grid[y][x].terrain = "wall"
        
        for _ in range(config["resource_clusters"]):
            x = self.rng.randint(0, self.GRID_SIZE - 1)
            y = self.rng.randint(0, self.GRID_SIZE - 1)
            game_map.add_resource(x, y)
    
    def _generate_crucible(self, game_map: Map):
        """Generate crucible map."""
        config = self.MAP_ARCHETYPES["crucible"]
        
        for y in range(self.GRID_SIZE):
            for x in range(self.GRID_SIZE):
                if self.rng.random() < config["wall_density"]:
                    game_map.grid[y][x].terrain = "wall"
        
        cx, cy = self.GRID_SIZE // 2, self.GRID_SIZE // 2
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                game_map.add_resource(cx + dx, cy + dy, Map.RESOURCE_TILE_MAX)
    
    def _generate_spawns(self, game_map: Map, num_players: int) -> List[Tuple[int, int]]:
        """Generate rotationally symmetric spawn positions."""
        positions = []
        quadrant_size = self.GRID_SIZE // 2
        
        base_spawn = (
            self.rng.randint(2, quadrant_size - 2),
            self.rng.randint(2, quadrant_size - 2)
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
