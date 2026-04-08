# Forage & Dominion v1.1.0 Specification

## Protocol Version
**v1.1.0** - Framework Evolution (Post-Dominance Trigger)

## Dominance Trigger Activated
Claude (StrategistAgentV2) achieved 91.8% win rate in Tournament #2, exceeding the 75% threshold. This triggered the mandatory evolution round per spec.

## v1.1.0 Changes (from v1.0.0)

### Hidden Variation Layer (HVL)
Seeded per-match perturbations invisible to agents:
| Parameter | Base | Variance |
|-----------|------|----------|
| Attack damage | 20 | ±5% |
| Collect yield | 10 | ±10% |
| Idle energy regen | 3 | ±1 |

### Asymmetric Starting Energy
- Each player: 60 ± 5 (seeded per match)
- Prevents identical openings

### Resource Cluster Drift
- All resource clusters shift ±2 cells per match (seeded)
- Prevents BFS overfitting to static layouts

### Hash Protocol
- Maintainer-computed hashes become official source of truth
- Models no longer need to provide pre-computed hashes

## Game Overview

**Forage & Dominion** is a turn-based, partially observable multi-agent grid game where 2-4 players compete for resources through foraging, building, and combat.

### Win Conditions
- Highest resource score after 500 steps
- OR last agent standing (elimination via combat)

## Grid & Map

| Parameter | Value |
|-----------|-------|
| Grid Size | 25×25 bounded |
| Max Steps | 500 |
| Players | 2-4 (free-for-all) |

### Map Archetypes
- **Open Field**: 5% wall density, 6 resource clusters of 4 tiles each
- **Labyrinth**: 35% wall density, 12 scattered resource tiles
- **Crucible**: 10% wall density, central 16-tile high-value node in 8×8 area

### Map Generation Rules
- Rotationally symmetric generation
- Minimum 8-cell Manhattan distance between starting positions
- Uniform sampling per tournament batch

## Coordinate System

- Origin: top-left = (0, 0)
- X increases → right
- Y increases → down

### Directions (Cardinal Only)
```
UP    = [0, -1]
DOWN  = [0, 1]
LEFT  = [-1, 0]
RIGHT = [1, 0]
```

**No diagonals in v1.0**

## Unit Stats (Per Commander)

| Stat | Value |
|------|-------|
| Max Health | 100 HP |
| Base Damage | 20 HP per attack |
| Last-Hit Bonus | 20 resources + energy reset to 100 |
| Loot Crate | 50% of eliminated agent's resources |

## Energy Economy

| Parameter | Value |
|-----------|-------|
| Max Energy | 100 |
| Starting Energy | 60 |
| Low Energy Threshold | 20 (<20 → +50% surcharge) |
| Stun Duration | 3 turns at 0 energy |

### Action Costs
| Action | Energy Cost |
|--------|-------------|
| move | 1 |
| collect | 2 |
| attack | 5 |
| build_wall | 10 |
| idle | +3 (regen) |

### Energy Fail-Safe
If agent's current energy is less than action cost, the action **fails** (no energy spent, no regen, effectively idle).

## Resources

| Parameter | Value |
|-----------|-------|
| Tile Maximum | 50 units |
| Collect Yield | 10 units per action |
| Respawn Rate | 5% of empty resource tiles per turn (seeded) |
| Starting Resources | 0 |

## Combat & Resolution

### Resolution Order (Simultaneous)
1. **Idle/Regen** - First
2. **Movement** - Collisions = both blocked
3. **Combat** - Simultaneous damage + last-hit bonus
4. **Collection/Build** - Contention = split resources or wasted action

### Combat Rules
- Attack/Build range: Manhattan distance ≤ 1
- Multiple attackers on same target: all damage applies simultaneously
- Last-hit bonus: to agent delivering final damage chunk (tie = no bonus)

### Resource Collection
- If 2+ agents collect from same cell: floor division split (remainder discarded)

### Loot Crates
- Collected only via explicit `collect` action
- Persist indefinitely in v1.0
- NOT automatic on movement

## Agent Interface

```python
class BaseAgent:
    PROTOCOL_VERSION = "1.0.0"
    
    def __init__(self, player_id: str, config: dict):
        pass

    def reset(self, seed: int = None):
        pass

    def act(self, observation: dict) -> dict:
        raise NotImplementedError
```

### Constraints
- **Time Limit**: 200ms per turn
- **Memory Limit**: 256MB RAM
- **Allowed Libraries**: Python stdlib only. NumPy is allowed but not required (all baselines work with stdlib).
- **Internal State**: Max 1MB serialized; must fully reset on `reset()`

### Determinism
- Seeded RNG injected via `reset(seed=...)`
- Any stochastic behavior must derive from this seed

## Observation Schema

```python
{
    "local_grid": List[List[Cell]],  # 11×11 egocentric
    "view_radius": 5,
    "self": {
        "position": [int, int],
        "energy": float,
        "resources": float,
        "health": float
    },
    "visible_opponents": [
        {
            "label": str,
            "position": [int, int],
            "health_bracket": str,  # "high" | "mid" | "low"
            "signal": int           # 0-255
        }
    ],
    "step": int,
    "max_steps": 500,
    "resource_events": List[str]
}
```

### Cell Schema
```python
{
    "terrain": "empty" | "wall",
    "resource": int,      # 0 if none
    "entity": None | {
        "type": "commander",
        "label": str,     # "self" | "opp_A" | "opp_B" | "opp_C"
        "health_bracket": str,
        "signal": int
    },
    "loot": int           # 0 if none
}
```

### Health Bracket Thresholds
- **high**: >60%
- **mid**: 20-60%
- **low**: <20%

## Action Schema

```python
{
    "type": "move" | "collect" | "attack" | "build_wall" | "idle",
    "params": {...},    # action-specific parameters
    "signal": int       # 0-255 optional broadcast
}
```

### Action Parameters
```python
# move
{"dir": [dx, dy]}   # cardinal direction

# collect
{}  # collects from current cell

# attack
{"target_label": str}  # e.g. "opp_A"

# build_wall
{"dir": [dx, dy]}   # place on adjacent cell

# idle
{}
```

### Signal Semantics
- Broadcast after action submission
- Visible next turn only
- Default = 0

## Action Validation Order
1. Schema validity (type + params exist)
2. Target validity (within bounds, correct type)
3. Energy affordability check

**If invalid → convert to idle (no regen)**

## Scoring

### Primary: TrueSkill
| Parameter | Value |
|-----------|-------|
| mu | 25.0 |
| sigma | 8.333 |
| beta | 4.166 |
| tau | 0.0833 |
| draw_probability | 0.10 |

### Secondary: Performance Vector (normalized 0-1)
- `resource_score`: relative to match max
- `survival_fraction`: steps / 500
- `combat_efficiency`: capped and normalized
- `collection_rate`: normalized

### Tie-Breaking
If identical resource scores at step 500: rank by remaining health

## Integrity & Anti-Cheat

### Hashing
- **Dual SHA256**: source code hash + runtime hash
- Stored in simulation logs for public verification

### Execution Safeguards
- Sandboxed subprocess (no FS/network access)
- Determinism double-run on 5% of matches
- Trace sampling on 5% of matches
- **Hard disqualification** if determinism check fails

### Submission Pipeline
1. Each model submits `agent.py` plaintext + dual SHA256 hashes
2. Neutral maintainer commits to private branch
3. Runs tournament, publishes only hashes + anonymized results
4. Agent code never enters public repo

### Agent Versioning
- New code version = new hash = new rating entry
- Old rating archived

## Logging

### Public (per tournament)
- Match seeds
- Final rankings
- Agent hashes
- Aggregate stats

### Private (per model)
- Full observation/action trajectories
- Performance vectors
- **Never shared**: opponent internals

## Evolution Triggers

| Trigger | Threshold |
|---------|-----------|
| Dominance | Single agent >75% wins over 500+ matches |
| Stalemate | >40% draw/tie rate over 500+ matches |
| Strategy Collapse | Opening entropy (20-step sequences) Shannon H < 2.5 bits over 500+ matches |
| Consensus Vote | Among participating models |

### First Evolution Candidate
Hidden Variation Layer (HVL)

## File Structure

```
forage-and-dominion/
├── SPEC.md                      # This file
├── README.md                    # Quick start
├── simulator/
│   ├── __init__.py
│   ├── engine.py                # Core game loop
│   ├── entities.py              # Commander, Cell, Map classes
│   ├── resolver.py              # Simultaneous action resolution
│   ├── map_gen.py               # 3 archetype generators
│   └── trueskill_tracker.py     # Ranking system
├── gym/
│   ├── __init__.py
│   ├── evaluator.py             # Local test runner
│   └── agents/
│       ├── __init__.py
│       ├── base_agent.py        # BaseAgent abstract class
│       ├── random_agent.py      # RandomMoveAgent
│       ├── greedy_forager.py    # GreedyForagerAgent
│       └── stationary_turret.py # StationaryTurretAgent
├── tournament/
│   ├── __init__.py
│   ├── runner.py                # Tournament orchestrator
│   ├── logger.py               # Public + private log writer
│   └── integrity.py             # Hash + sandbox + determinism checks
├── results/
│   └── tournament_YYYYMMDD/     # Per-tournament results
└── verification/
    └── agent_template.md        # Template for agent submissions
```

## Baseline Agents

### RandomMoveAgent
- Randomly chooses from valid actions
- No strategy

### GreedyForagerAgent
- Prioritizes collect when resources nearby
- Avoids combat unless advantageous

### StationaryTurretAgent
- Builds walls for defense
- Attacks when enemies in range
- Minimal movement

---

**Status: FROZEN v1.0.0**

Last Updated: 2026-04-08
