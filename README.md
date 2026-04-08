# Forage & Dominion

Multi-agent competitive simulation framework for AI agents.

## Version
**v1.0.0** - Protocol Frozen — agent submissions now open.

## Quick Start

```python
from simulator.engine import Engine
from gym.agents.random_agent import RandomMoveAgent
from gym.agents.greedy_forager import GreedyForagerAgent

# Create agents
agents = [
    RandomMoveAgent("agent_A", {}),
    GreedyForagerAgent("agent_B", {}),
]

# Run match
engine = Engine()
result = engine.run_match(agents, match_id=0, archetype="open_field")

print(f"Winners: {result.winners}")
print(f"Rankings: {result.rankings}")
```

## Structure

```
forage-and-dominion/
├── SPEC.md              # Full specification
├── CHECKSUMS.md         # File checksums
├── UNCERTAINTIES.md     # Open items for clarification
├── simulator/           # Core game engine
│   ├── engine.py
│   ├── entities.py
│   ├── map_gen.py
│   └── resolver.py
├── gym/
│   └── agents/          # Baseline agents
│       ├── base_agent.py
│       ├── random_agent.py
│       ├── greedy_forager.py
│       └── stationary_turret.py
├── tournament/
│   ├── runner.py
│   ├── logger.py
│   └── integrity.py
└── verification/
    └── agent_template.md
```

## Protocol

See SPEC.md for full protocol documentation.

## Checksums

All files are versioned with `PROTOCOL_VERSION = "1.0.0"`. See CHECKSUMS.md for file integrity verification.
