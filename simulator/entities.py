"""
Forage & Dominion - Entity Classes
Version: 1.2.0
"""
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Any
import random


PROTOCOL_VERSION = "1.2.0"


@dataclass
class Commander:
    """Represents a player commander in the game."""
    label: str
    position: Tuple[int, int]
    health: float = 100.0
    energy: float = 60.0
    resources: float = 0.0
    walls_placed: int = 0
    stunned_turns: int = 0
    last_signal: int = 0
    alive: bool = True
    base_damage: float = 20.0
    
    MAX_HEALTH = 100.0
    MAX_ENERGY = 100.0
    STARTING_ENERGY = 60.0
    LOW_ENERGY_THRESHOLD = 20.0
    
    BASE_DAMAGE = 20.0
    LAST_HIT_BONUS_RESOURCES = 20
    LOOT_CRATE_PERCENT = 0.5
    
    ENERGY_COSTS = {
        "move": 1,
        "collect": 2,
        "attack": 5,
        "build_wall": 10,
    }
    ENERGY_REGEN = 3
    LOW_ENERGY_SURCHARGE = 1.5
    STUN_DURATION = 3
    
    _base_damage: float = field(default=BASE_DAMAGE, init=False, repr=False)
    _energy_regen: int = field(default=ENERGY_REGEN, init=False, repr=False)
    
    def __post_init__(self):
        object.__setattr__(self, '_base_damage', self.base_damage if self.base_damage else self.BASE_DAMAGE)
        object.__setattr__(self, '_energy_regen', self.ENERGY_REGEN)
    
    def set_base_damage(self, damage: float):
        """Set base damage (for HVL)."""
        object.__setattr__(self, '_base_damage', damage)
    
    def set_energy_regen(self, regen: int):
        """Set energy regen (for HVL)."""
        object.__setattr__(self, '_energy_regen', regen)
    
    def get_health_bracket(self) -> str:
        """Return health bracket category."""
        pct = self.health / self.MAX_HEALTH
        if pct > 0.6:
            return "high"
        elif pct >= 0.2:
            return "mid"
        return "low"
    
    def get_energy_cost(self, action_type: str) -> float:
        """Calculate energy cost with low-energy surcharge."""
        base_cost = self.ENERGY_COSTS.get(action_type, 0)
        if self.energy < self.LOW_ENERGY_THRESHOLD and action_type != "idle":
            return base_cost * self.LOW_ENERGY_SURCHARGE
        return base_cost
    
    def take_damage(self, amount: float):
        """Apply damage to commander."""
        self.health = max(0, self.health - amount)
        if self.health <= 0:
            self.alive = False
    
    def can_afford(self, action_type: str) -> bool:
        """Check if commander can afford the action."""
        return self.energy >= self.get_energy_cost(action_type)
    
    def get_damage(self) -> float:
        """Get base damage (supports HVL)."""
        return self._base_damage
    
    def apply_action(self, action_type: str):
        """Deduct energy for action (without checking affordability)."""
        if action_type == "idle":
            self.energy = min(self.MAX_ENERGY, self.energy + self._energy_regen)
        else:
            cost = self.get_energy_cost(action_type)
            self.energy = max(0, self.energy - cost)
            
    def apply_stun(self):
        """Apply stun if energy depleted."""
        if self.energy <= 0:
            self.stunned_turns = self.STUN_DURATION
    
    def decrement_stun(self):
        """Decrement stun counter."""
        if self.stunned_turns > 0:
            self.stunned_turns -= 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to observation dict."""
        return {
            "position": list(self.position),
            "energy": self.energy,
            "resources": self.resources,
            "health": self.health,
        }


@dataclass
class Cell:
    """Represents a single grid cell."""
    terrain: str = "empty"
    resource: int = 0
    entity: Optional[Dict[str, Any]] = None
    loot: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict."""
        return {
            "terrain": self.terrain,
            "resource": self.resource,
            "entity": self.entity,
            "loot": self.loot,
        }
    
    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Cell":
        """Deserialize from dict."""
        return Cell(
            terrain=d.get("terrain", "empty"),
            resource=d.get("resource", 0),
            entity=d.get("entity"),
            loot=d.get("loot", 0),
        )


class Map:
    """Represents the game map."""
    
    GRID_SIZE = 25
    MAX_STEPS = 500
    RESOURCE_TILE_MAX = 50
    COLLECT_YIELD = 10
    RESPAWN_RATE = 0.05
    RESPAWN_INC_RATE = 0.15
    LOOT_DECAY_RATE = 0.05
    
    def __init__(self, rng: random.Random):
        self.rng = rng
        self.grid: List[List[Cell]] = [[Cell() for _ in range(self.GRID_SIZE)] 
                                         for _ in range(self.GRID_SIZE)]
        self._respawn_chance = 0.0
    
    def in_bounds(self, x: int, y: int) -> bool:
        """Check if coordinates are within bounds."""
        return 0 <= x < self.GRID_SIZE and 0 <= y < self.GRID_SIZE
    
    def is_wall(self, x: int, y: int) -> bool:
        """Check if cell is a wall."""
        if not self.in_bounds(x, y):
            return True
        return self.grid[y][x].terrain == "wall"
    
    def place_wall(self, x: int, y: int) -> bool:
        """Place a wall at position. Returns success."""
        if not self.in_bounds(x, y):
            return False
        if self.grid[y][x].terrain != "empty" or self.grid[y][x].entity is not None:
            return False
        self.grid[y][x].terrain = "wall"
        return True
    
    def add_resource(self, x: int, y: int, amount: int = None):
        """Add resource to cell."""
        if not self.in_bounds(x, y):
            return
        if amount is None:
            amount = self.rng.randint(1, self.RESOURCE_TILE_MAX)
        self.grid[y][x].resource = min(self.RESOURCE_TILE_MAX, 
                                        self.grid[y][x].resource + amount)
    
    def collect_resource(self, x: int, y: int) -> int:
        """Collect resource from cell. Returns amount collected."""
        if not self.in_bounds(x, y):
            return 0
        cell = self.grid[y][x]
        if cell.resource <= 0 and cell.loot <= 0:
            return 0
        
        available = cell.resource + cell.loot
        yield_amount = min(self.COLLECT_YIELD, available)
        
        cell.resource = max(0, cell.resource - yield_amount)
        
        return yield_amount
    
    def add_loot(self, x: int, y: int, amount: int):
        """Add loot to cell."""
        if not self.in_bounds(x, y):
            return
        self.grid[y][x].loot += amount
    
    def respawn_resources(self):
        """Respawn resources on empty tiles with probabilistic window."""
        self._respawn_chance = min(1.0, self._respawn_chance + self.RESPAWN_INC_RATE)
        
        empty_cells = []
        for y in range(self.GRID_SIZE):
            for x in range(self.GRID_SIZE):
                cell = self.grid[y][x]
                if cell.terrain == "empty" and cell.resource == 0 and cell.entity is None:
                    empty_cells.append((x, y))
        
        if not empty_cells:
            return
        
        if self.rng.random() < self._respawn_chance:
            respawn_count = max(1, int(len(empty_cells) * self.RESPAWN_RATE))
            for _ in range(respawn_count):
                if not empty_cells:
                    break
                idx = self.rng.randint(0, len(empty_cells) - 1)
                x, y = empty_cells.pop(idx)
                self.add_resource(x, y)
    
    def decay_loot(self):
        """Apply loot decay to all loot tiles."""
        for y in range(self.GRID_SIZE):
            for x in range(self.GRID_SIZE):
                cell = self.grid[y][x]
                if cell.loot > 0:
                    decay = max(1, int(cell.loot * self.LOOT_DECAY_RATE))
                    cell.loot = max(0, cell.loot - decay)
    
    def get_egocentric_view(self, pos: Tuple[int, int], radius: int) -> List[List[Cell]]:
        """Get egocentric view of the map."""
        px, py = pos
        view = []
        for dy in range(-radius, radius + 1):
            row = []
            for dx in range(-radius, radius + 1):
                x, y = px + dx, py + dy
                if not self.in_bounds(x, y):
                    row.append(Cell(terrain="wall"))
                else:
                    row.append(self.grid[y][x])
            view.append(row)
        return view
    
    def has_line_of_sight(self, from_pos: Tuple[int, int], 
                          to_pos: Tuple[int, int]) -> bool:
        """Check if there's LOS between two positions (walls block)."""
        fx, fy = from_pos
        tx, ty = to_pos
        
        dx = abs(tx - fx)
        dy = abs(ty - fy)
        sx = 1 if fx < tx else -1
        sy = 1 if fy < ty else -1
        err = dx - dy
        
        x, y = fx, fy
        while (x, y) != (tx, ty):
            if x != fx or y != fy:
                if self.is_wall(x, y):
                    return False
            if dx > dy:
                err -= dy
                if err < 0:
                    err += dx
                    y += sy
                x += sx
            else:
                err -= dx
                if err < 0:
                    err += dy
                    x += sx
                y += sy
        return True
