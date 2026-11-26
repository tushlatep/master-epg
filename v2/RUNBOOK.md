# Master EPG V2 runbook (development)
## Operating rules
Never substitute national, sister, regional or time-shift feeds. Exact verified identity only. Keep playlist and registry private. Do not publish upstream schedules without permission.
## Baseline
Production diagnostic run 45749352657; alternative source benchmark 45749470177. Benchmark artifacts contain source channel catalogs and future programme counts, not full schedule quality.
## Tests
Run python -m unittest discover -s v2 -p 'test_*.py' -v. CI run 45751428973 passed.
## Local audit
Extract benchmark artifact into a catalog directory. Prepare private registry JSON keyed by exact playlist channel name, with a list of source, id and identity_evidence objects. Run python v2/strict_match.py channels.csv catalog_dir registry.json audit.json. Review every unapproved candidate; no automatic approval.
## Deployment gates
Pending: real schedule continuity benchmark, verified private registry, source rights, delivery design, end-to-end TiviMate validation. No production deployment authorized by this runbook.
## Recovery
Keep main and its Pages configuration unchanged during V2 development. Do not publish stale or empty schedules. Investigate source errors and use only verified same-identity alternatives.
