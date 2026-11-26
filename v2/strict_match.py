"""Local audit of benchmark catalogs. Never infer identity from a logo."""
import csv
import json
import sys
from pathlib import Path
from collections import defaultdict

def normalize(name):
    return " ".join(name.casefold().split())

def audit(playlist, catalogs, verified):
    index = defaultdict(list)
    by_id = defaultdict(list)
    for source, records in catalogs.items():
        for record in records:
            if not record.get("id") or record.get("future", 0) <= 0:
                continue
            by_id[(source, str(record["id"]))].append(record)
            for name in set(normalize(n) for n in record.get("names", []) if n):
                index[name].append((source, str(record["id"])))
    out = []
    for channel in playlist:
        name = channel["channel_name"]
        approved = []
        for mapping in verified.get(name, []):
            source, cid = mapping["source"], str(mapping["id"])
            if not mapping.get("identity_evidence"):
                continue
            records = by_id.get((source, cid), [])
            if len(records) == 1:
                approved.append((source, cid))
        candidates = sorted(set(index.get(normalize(name), [])))
        status = "verified_identity_current" if approved else ("review_required" if candidates else "unmatched")
        out.append({"channel_number": channel["channel_number"], "channel_name":name,
                    "status":status,"approved":approved,"candidates":candidates})
    return out

def main():
    playlist, catalog_dir, registry, output = map(Path, sys.argv[1:])
    with playlist.open(newline="", encoding="utf-8-sig") as f:
        channels = list(csv.DictReader(f))
    catalogs = {}
    for p in catalog_dir.glob("*.json"):
        data = json.loads(p.read_text())
        if isinstance(data, list):
            catalogs[p.stem] = data
    result = audit(channels, catalogs, json.loads(registry.read_text()))
    output.write_text(json.dumps(result, indent=2))
    from collections import Counter
    print(dict(Counter(r["status"] for r in result)))

if __name__ == "__main__":
    main()
