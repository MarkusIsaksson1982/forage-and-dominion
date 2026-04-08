# Uncertainties and Open Items

This document tracks items that require clarification before or during implementation.

## Version 1.0.0 - Pending Clarifications

### 1. Cross-Platform Execution
- **Issue**: Timeout enforcement via `signal` + `multiprocessing` may not work consistently on Windows
- **Status**: Need to verify cross-platform compatibility for 200ms timeout
- **Impact**: May require alternative timeout mechanism (e.g., subprocess with timeout)

### 2. NumPy Dependency
- **Issue**: The spec says "NumPy + StdLib only" but some baseline agents don't use NumPy
- **Status**: Clarify if NumPy is actually required or just allowed
- **Impact**: Currently all code works with stdlib only

### 3. Hidden Variation Layer (HVL)
- **Issue**: ChatGPT proposed HVL but it was deferred to evolution
- **Status**: Not implemented in v1.0
- **Impact**: Future evolution candidate

### 4. Strategy Collapse Detection
- **Issue**: Requires computing Shannon entropy of 20-step action sequences across tournament
- **Status**: Algorithm defined but not yet implemented
- **Impact**: Evolution trigger not fully operational

### 5. Subprocess Isolation Details
- **Issue**: Need to verify that sandboxing actually prevents file system and network access
- **Status**: Not tested/implemented
- **Impact**: Security of agent isolation

### 6. Trace Sampling Implementation
- **Issue**: Need to implement actual logging of observations/actions on 5% of matches
- **Status**: Not implemented
- **Impact**: Anti-cheat verification incomplete

### 7. Resource Event System
- **Issue**: Observation includes `resource_events` but spec doesn't define event types
- **Status**: Needs definition
- **Impact**: Observation incomplete

### 8. Visualizer/Replay Tool
- **Issue**: Spec mentions optional replay viewer but not implemented
- **Status**: Not implemented
- **Impact**: Debugging and viewing matches not possible

### 9. Test Coverage
- **Issue**: No unit tests included
- **Status**: Should be added before tournament
- **Impact**: Reliability of simulator

### 10. Exact Match Seed Publication
- **Issue**: Spec says seeds published pre-run but tournament runner generates them during run
- **Status**: Need workflow adjustment
- **Impact**: Reproducibility

---

## Clarification Requests

Please clarify these items before the inaugural tournament:

1. Should `resource_events` be populated? If so, with what?
2. Is Windows timeout handling acceptable?
3. Should HVL be implemented for v1.0 instead of deferred?
4. What is the exact format for agent code submission?

---

**Document Status**: OPEN - Requires clarification
