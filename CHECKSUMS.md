# Forage & Dominion v1.0.0 - File Checksums

This document contains SHA256 checksums for all files in the framework.

## Protocol Version: 1.0.0

Generated: 2026-04-08

---

## Python Source Files

| SHA256 Hash | File Path |
|-------------|-----------|
| D6E2170139117C6BA36CC3BDADBB2B3779AD71B131AEC55F9566BEDE24EFF5D8 | gym\evaluator.py |
| A900BBC345AE16F18B5E9B59620D6C78884F7909B41027A94643FC521E8297F5 | gym\__init__.py |
| 30FDD766B758B938C1519E921F6572A830C61533BACFEDD84827C70D010DBC9D | gym\agents\base_agent.py |
| E9C2B130D5D41479A0745B1F6BF1ACFB3747BA5B51A9C0FE7B582789B8E4919D | gym\agents\greedy_forager.py |
| 9DA54E99864F4BC6C4E1F39DDD41DBECE4F7B7644BF6C7ED1FBAF114FA300C8C | gym\agents\random_agent.py |
| 903C28790B95472F5FEB132A484ABFF9CAA30EC89A35BBC16975D57CCC5721AD | gym\agents\stationary_turret.py |
| CBEC86DE13EE1053E6CC98CE816185E18431DD027346CF5BB254FE935FF0B4CA | gym\agents\__init__.py |
| DEDB71D8B7FF29CFB7C534CD70E09A3F4D7D21F3E9ABFBC588B6D20B411BB944 | simulator\engine.py |
| B6883C34611DCA878C185196D9A76B0FEC6DA39297095BF9CDF4ABA68B09E817 | simulator\entities.py |
| 515120975A80DE5AF5D8110755595D2C5D7E84E1C05658632FDB99B13C2ACE1F | simulator\map_gen.py |
| E2A58284E4EED74A60A887859A98957CD25AA89436FA26A73378A588EB9C454D | simulator\resolver.py |
| A08FFA11B7767EBC06D683C56005693BBF300F7945DD2DBEC29ADEF6A02949AD | simulator\trueskill_tracker.py |
| 23AA23E1B7DA77DD9288330825B6CB483A5B7116183624FECF06A1F218B0027F | simulator\__init__.py |
| 59E2814DA0ADA61481617BF93316769764640E94AA28282F1EF0BAC4AFD469EA | tournament\integrity.py |
| 6488C4847AFF5E7343E56AEBFBBA66AEE047CCD78D1E6D66526E29A46E5A38F2 | tournament\logger.py |
| C7CCEF4A8F4B4138A0C421850182646C800B0E1F5F418444063F5E5E162FC669 | tournament\runner.py |
| 8E9F6BBDB28730829909477C20F2729DEEBC0290DC9F5D2DD3D41C2228361349 | tournament\__init__.py |

---

## Documentation Files

| SHA256 Hash | File Path |
|-------------|-----------|
| (See git) | SPEC.md |
| (See git) | UNCERTAINTIES.md |
| (See git) | verification\agent_template.md |

---

## Verification Instructions

To verify file integrity:

```powershell
# Verify a single file
Get-FileHash -Path "path\to\file.py" -Algorithm SHA256

# Verify all Python files
Get-ChildItem -Path "forage-and-dominion" -Recurse -Filter "*.py" -File | ForEach-Object { 
    $hash = Get-FileHash -Path $_.FullName -Algorithm SHA256
    Write-Host "$($hash.Hash)  $($_.Name)"
}
```

---

## Version History

| Version | Date | Notes |
|---------|------|-------|
| 1.0.0 | 2026-04-08 | Initial frozen spec |
