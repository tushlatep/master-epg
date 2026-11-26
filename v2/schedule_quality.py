from datetime import datetime, timedelta, timezone

def parse(value):
    return datetime.strptime(value, "%Y%m%d%H%M%S %z")

def quality(programmes, now=None, hours=24):
    now = now or datetime.now(timezone.utc)
    end = now + timedelta(hours=hours)
    intervals = set()
    invalid = duplicates = 0
    for p in programmes:
        try:
            a,b = parse(p.get("start","")),parse(p.get("stop",""))
            if b <= a: raise ValueError("invalid interval")
        except (ValueError, TypeError):
            invalid += 1
            continue
        if b <= now or a >= end: continue
        pair = (max(a,now),min(b,end))
        if pair in intervals: duplicates += 1
        intervals.add(pair)
    cursor = now
    covered = overlap = largest_gap = 0
    for a,b in sorted(intervals):
        largest_gap = max(largest_gap,(a-cursor).total_seconds())
        overlap += max(0,(min(b,cursor)-a).total_seconds())
        covered += max(0,(b-max(a,cursor)).total_seconds())
        cursor = max(cursor,b)
    largest_gap = max(largest_gap,(end-cursor).total_seconds())
    return {"coverage_pct":round(100*covered/(hours*3600),2),
            "largest_gap_minutes":round(largest_gap/60,2),
            "overlap_minutes":round(overlap/60,2),
            "invalid":invalid,"duplicate_intervals":duplicates,
            "current":any(a<=now<b for a,b in intervals)}
