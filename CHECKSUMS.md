# Forage & Dominion v1.1.0 - File Checksums

This document contains SHA256 checksums for all files in the framework v1.1.0.

## Protocol Version: 1.1.0

Generated: 2026-04-09

## Dominance Trigger Note
Claude achieved 91.8% win rate in Tournament #2, exceeding the 75% threshold. This triggered the mandatory evolution round per spec.

---

## Python Source Files

| SHA256 Hash | File Path |
|-------------|-----------|
| D6E2170139117C6BA36CC3BDADBB2B3779AD71B131AEC55F9566BEDE24EFF5D8 | gym\evaluator.py |
| F440520B2AE634970FF2111FEDA7B3AD31EFADDEDDEF4960F4E37DACD380C493 | gym\__init__.py |
| 9DECD94F4A7305CC52B242DFD84034A2C0DEA5CA69FD4AA2ADE4503AE02F635A | gym\agents\base_agent.py |
| E9C2B130D5D41479A0745B1F6BF1ACFB3747BA5B51A9C0FE7B582789B8E4919D | gym\agents\greedy_forager.py |
| 9DA54E99864F4BC6C4E1F39DDD41DBECE4F7B7644BF6C7ED1FBAF114FA300C8C | gym\agents\random_agent.py |
| 903C28790B95472F5FEB132A484ABFF9CAA30EC89A35BBC16975D57CCC5721AD | gym\agents\stationary_turret.py |
| 861C39D48FE6451E21777B7F717F8A1ABCE1E48661FF5C532038BB9E99CE023C | gym\agents\__init__.py |
| 6A7CF66FA57602D337A9B33EA1CE97FDED4683049353D26C9436B56AEE56B678 | simulator\engine.py |
| FE509B36B5373E995A86DE596A2EC60DC57B7C760053B8C007DC10C217B03957 | simulator\entities.py |
| B169A4E2F467738EBD350492BED2EBD92F62CA02A822C80F2E4FF3B50E1762E6 | simulator\map_gen.py |
| F456A1646D801CD1C4DC15E161ADB343466C53F9A6D341E3B1FC7D5167764967 | simulator\resolver.py |
| AB51B1979B10FCBC90BDD1DC299F86FB1B0935A9359B230E6BBC834621894012 | simulator\trueskill_tracker.py |
| C75D7343A9014126A9975803864746AF390C8EC27FE592ADBF467F83A7C1E885 | simulator\__init__.py |
| 59E2814DA0ADA61481617BF93316769764640E94AA28282F1EF0BAC4AFD469EA | tournament\integrity.py |
| D4F568B7AEEE703F6BAA79A1B564840A3E86BCB717A99405D19673DC2A9E0D82 | tournament\logger.py |
| C7CCEF4A8F4B4138A0C421850182646C800B0E1F5F418444063F5E5E162FC669 | tournament\runner.py |
| 702311EB834A14BAD889466E8D71EFD34B76E5F5C3BCD9969DCEAD24A65F2EF9 | tournament\__init__.py |

---

## v1.1.0 Changes from v1.0.0

### Hidden Variation Layer (HVL)
- Attack damage: ±5% variance (seeded)
- Collect yield: ±10% variance (seeded)  
- Idle energy regen: ±1 variance (seeded)

### Asymmetric Starting Energy
- 60 ± 5 (seeded per match)

### Resource Cluster Drift
- ±2 cell shift per match (seeded)

### Hash Protocol
- Maintainer-computed hashes now official source of truth

---

## Verification Instructions

```powershell
Get-FileHash -Path "forage-and-dominion\simulator\engine.py" -Algorithm SHA256
```

---

## Version History

| Version | Date | Notes |
|---------|------|-------|
| 1.0.0 | 2026-04-08 | Initial frozen spec |
| 1.1.0 | 2026-04-09 | Post-dominance evolution (HVL + drift + energy) |