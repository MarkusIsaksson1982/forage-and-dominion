"""
Forage & Dominion - Action Resolver
Version: 1.1.0
"""
from typing import List, Tuple, Dict, Any, Set, Optional
from dataclasses import dataclass
from simulator.entities import Commander, Map


PROTOCOL_VERSION = "1.1.0"


@dataclass
class ActionResult:
    """Result of a single action."""
    commander_label: str
    action_type: str
    success: bool
    energy_spent: float
    damage_dealt: float = 0.0
    damage_taken: float = 0.0
    resources_gained: float = 0.0
    error: str = ""


class Resolver:
    """Handles simultaneous action resolution."""
    
    DIRECTIONS = {
        (0, -1): "UP",
        (0, 1): "DOWN",
        (-1, 0): "LEFT",
        (1, 0): "RIGHT",
    }
    
    def __init__(self):
        pass
    
    def resolve(self, commanders: List[Commander], game_map: Map,
                actions: Dict[str, Dict[str, Any]],
                hvl: Optional[Any] = None) -> List[ActionResult]:
        """
        Resolve all actions simultaneously.
        
        Resolution order:
        1. Idle/Regen
        2. Movement
        3. Combat
        4. Collection/Build
        """
        results = []
        
        validated_actions = self._validate_actions(commanders, actions)
        
        idle_results = self._resolve_idle(commanders, validated_actions, hvl)
        results.extend(idle_results)
        
        movement_results = self._resolve_movement(commanders, game_map, validated_actions)
        results.extend(movement_results)
        
        combat_results = self._resolve_combat(commanders, game_map, validated_actions, hvl)
        results.extend(combat_results)
        
        collection_results = self._resolve_collection(commanders, game_map, validated_actions)
        results.extend(collection_results)
        
        build_results = self._resolve_build(commanders, game_map, validated_actions)
        results.extend(build_results)
        
        return results
    
    def _validate_actions(self, commanders: List[Commander],
                         actions: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Validate and sanitize actions."""
        validated = {}
        cmd_map = {c.label: c for c in commanders}
        
        for cmd in commanders:
            if not cmd.alive:
                continue
                
            action = actions.get(cmd.label, {})
            action_type = action.get("type", "idle")
            params = action.get("params", {})
            
            if cmd.stunned_turns > 0:
                action_type = "idle"
                params = {}
            
            if action_type not in ["move", "collect", "attack", "build_wall", "idle"]:
                action_type = "idle"
                params = {}
            
            if action_type == "move":
                direction = params.get("dir")
                if direction is None or tuple(direction) not in self.DIRECTIONS:
                    action_type = "idle"
                    params = {}
                    
            elif action_type == "attack":
                target = params.get("target_label")
                if target not in cmd_map:
                    action_type = "idle"
                    params = {}
                    
            elif action_type == "build_wall":
                direction = params.get("dir")
                if direction is None or tuple(direction) not in self.DIRECTIONS:
                    action_type = "idle"
                    params = {}
            
            if not cmd.can_afford(action_type):
                action_type = "idle"
                params = {}
            
            validated[cmd.label] = {
                "type": action_type,
                "params": params,
                "signal": action.get("signal", 0),
            }
        
        return validated
    
    def _resolve_idle(self, commanders: List[Commander],
                     actions: Dict[str, Dict[str, Any]],
                     hvl: Optional[Any] = None) -> List[ActionResult]:
        """Handle idle/regen phase."""
        results = []
        regen = hvl.get_regen() if hvl else 3
        
        for cmd in commanders:
            if not cmd.alive:
                continue
                
            action = actions.get(cmd.label, {})
            action_type = action.get("type", "idle")
            
            if action_type == "idle":
                cmd.apply_action("idle")
                cmd._energy_regen = regen
                results.append(ActionResult(
                    commander_label=cmd.label,
                    action_type="idle",
                    success=True,
                    energy_spent=-regen,
                ))
            else:
                results.append(ActionResult(
                    commander_label=cmd.label,
                    action_type=action_type,
                    success=True,
                    energy_spent=0,
                ))
        
        return results
    
    def _resolve_movement(self, commanders: List[Commander], game_map: Map,
                         actions: Dict[str, Dict[str, Any]]) -> List[ActionResult]:
        """Handle movement phase."""
        results = []
        proposed_moves: Dict[Tuple[int, int], List[str]] = {}
        
        for cmd in commanders:
            if not cmd.alive:
                continue
                
            action = actions.get(cmd.label, {})
            action_type = action.get("type", "idle")
            
            if action_type != "move":
                results.append(ActionResult(
                    commander_label=cmd.label,
                    action_type=action_type,
                    success=True,
                    energy_spent=0,
                ))
                continue
            
            direction = action.get("params", {}).get("dir")
            if direction is None:
                results.append(ActionResult(
                    commander_label=cmd.label,
                    action_type="move",
                    success=False,
                    energy_spent=0,
                    error="No direction",
                ))
                continue
            
            dx, dy = direction
            new_x = cmd.position[0] + dx
            new_y = cmd.position[1] + dy
            
            if not game_map.in_bounds(new_x, new_y):
                results.append(ActionResult(
                    commander_label=cmd.label,
                    action_type="move",
                    success=False,
                    energy_spent=0,
                    error="Out of bounds",
                ))
                continue
            
            if game_map.is_wall(new_x, new_y):
                results.append(ActionResult(
                    commander_label=cmd.label,
                    action_type="move",
                    success=False,
                    energy_spent=0,
                    error="Blocked by wall",
                ))
                continue
            
            proposed_moves.setdefault((new_x, new_y), []).append(cmd.label)
        
        moved_players = set()
        for cmd in commanders:
            if not cmd.alive:
                continue
                
            action = actions.get(cmd.label, {})
            action_type = action.get("type", "idle")
            
            if action_type != "move":
                continue
            
            direction = action.get("params", {}).get("dir")
            dx, dy = direction
            new_x = cmd.position[0] + dx
            new_y = cmd.position[1] + dy
            
            if proposed_moves.get((new_x, new_y), []) != [cmd.label]:
                results.append(ActionResult(
                    commander_label=cmd.label,
                    action_type="move",
                    success=False,
                    energy_spent=0,
                    error="Collision",
                ))
                continue
            
            cmd.position = (new_x, new_y)
            moved_players.add(cmd.label)
            
            cost = cmd.get_energy_cost("move")
            cmd.energy -= cost
            
            results.append(ActionResult(
                commander_label=cmd.label,
                action_type="move",
                success=True,
                energy_spent=cost,
            ))
        
        return results
    
    def _resolve_combat(self, commanders: List[Commander], game_map: Map,
                        actions: Dict[str, Dict[str, Any]],
                        hvl: Optional[Any] = None) -> List[ActionResult]:
        """Handle combat phase."""
        results = []
        attacks: Dict[str, List[Tuple[str, float]]] = {}
        cmd_positions = {c.label: c.position for c in commanders if c.alive}
        cmd_map = {c.label: c for c in commanders}
        
        for cmd in commanders:
            if not cmd.alive:
                continue
                
            action = actions.get(cmd.label, {})
            action_type = action.get("type", "idle")
            
            if action_type != "attack":
                continue
             
            target_label = action.get("params", {}).get("target_label")
            if target_label is None:
                continue
            
            target = cmd_map.get(target_label)
            if target is None or not target.alive:
                continue
            
            dist = abs(cmd.position[0] - target.position[0]) + abs(cmd.position[1] - target.position[1])
            if dist > 1:
                continue
            
            damage = cmd.get_damage()
            cost = cmd.get_energy_cost("attack")
            cmd.energy -= cost
            
            attacks.setdefault(target_label, []).append((cmd.label, damage))
            
            results.append(ActionResult(
                commander_label=cmd.label,
                action_type="attack",
                success=True,
                energy_spent=cost,
                damage_dealt=damage,
            ))
        
        for target_label, attackers in attacks.items():
            target = cmd_map.get(target_label)
            if target is None:
                continue
            
            total_damage = sum(d for _, d in attackers)
            target.take_damage(total_damage)
            
            surviving = [a for a, d in attackers if cmd_map[a].alive]
            if target.health <= 0:
                for attacker_label in surviving:
                    attacker = cmd_map.get(attacker_label)
                    if attacker and attacker.alive:
                        attacker.resources += Commander.LAST_HIT_BONUS_RESOURCES
                        attacker.energy = Commander.MAX_ENERGY
                
                loot_amount = int(target.resources * Commander.LOOT_CRATE_PERCENT)
                game_map.add_loot(target.position[0], target.position[1], loot_amount)
        
        return results
    
    def _resolve_collection(self, commanders: List[Commander], game_map: Map,
                          actions: Dict[str, Dict[str, Any]],
                          hvl: Optional[Any] = None) -> List[ActionResult]:
        """Handle resource collection."""
        results = []
        collectors: Dict[Tuple[int, int], List[str]] = {}
        yield_amount = hvl.get_yield() if hvl else 10
        
        for cmd in commanders:
            if not cmd.alive:
                continue
                
            action = actions.get(cmd.label, {})
            action_type = action.get("type", "idle")
            
            if action_type != "collect":
                continue
            
            collectors.setdefault(cmd.position, []).append(cmd.label)
        
        for pos, collector_labels in collectors.items():
            cell = game_map.grid[pos[1]][pos[0]]
            available = cell.resource + cell.loot
            
            if available <= 0:
                for label in collector_labels:
                    results.append(ActionResult(
                        commander_label=label,
                        action_type="collect",
                        success=False,
                        energy_spent=0,
                        error="No resources",
                    ))
                continue
            
            per_collector = min(yield_amount, available // len(collector_labels))
            
            for label in collector_labels:
                cmd = next((c for c in commanders if c.label == label), None)
                if cmd is None:
                    continue
                    
                cmd.resources += per_collector
                cost = cmd.get_energy_cost("collect")
                cmd.energy -= cost
                
                results.append(ActionResult(
                    commander_label=label,
                    action_type="collect",
                    success=True,
                    energy_spent=cost,
                    resources_gained=per_collector,
                ))
            
            collected = per_collector * len(collector_labels)
            cell.resource = max(0, cell.resource - collected)
            cell.loot = max(0, cell.loot - collected)
        
        return results
    
    def _resolve_build(self, commanders: List[Commander], game_map: Map,
                      actions: Dict[str, Dict[str, Any]]) -> List[ActionResult]:
        """Handle wall building."""
        results = []
        build_attempts: Dict[Tuple[int, int], List[str]] = {}
        
        for cmd in commanders:
            if not cmd.alive:
                continue
                
            action = actions.get(cmd.label, {})
            action_type = action.get("type", "idle")
            
            if action_type != "build_wall":
                continue
            
            direction = action.get("params", {}).get("dir")
            if direction is None:
                continue
            
            dx, dy = direction
            bx = cmd.position[0] + dx
            by = cmd.position[1] + dy
            
            if not game_map.in_bounds(bx, by):
                results.append(ActionResult(
                    commander_label=cmd.label,
                    action_type="build_wall",
                    success=False,
                    energy_spent=0,
                    error="Out of bounds",
                ))
                continue
            
            build_attempts.setdefault((bx, by), []).append(cmd.label)
        
        for pos, builder_labels in build_attempts.items():
            if len(builder_labels) > 1:
                for label in builder_labels:
                    results.append(ActionResult(
                        commander_label=label,
                        action_type="build_wall",
                        success=False,
                        energy_spent=0,
                        error="Conflict",
                    ))
                continue
            
            builder_label = builder_labels[0]
            cmd = next((c for c in commanders if c.label == builder_label), None)
            if cmd is None:
                continue
            
            success = game_map.place_wall(pos[0], pos[1])
            if success:
                cost = cmd.get_energy_cost("build_wall")
                cmd.energy -= cost
                cmd.walls_placed += 1
                
                results.append(ActionResult(
                    commander_label=builder_label,
                    action_type="build_wall",
                    success=True,
                    energy_spent=cost,
                ))
            else:
                results.append(ActionResult(
                    commander_label=builder_label,
                    action_type="build_wall",
                    success=False,
                    energy_spent=0,
                    error="Invalid position",
                ))
        
        return results
