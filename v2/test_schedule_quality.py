import unittest
from datetime import datetime,timezone
from v2.schedule_quality import quality
class QualityTests(unittest.TestCase):
    def test_full(self):
        now=datetime(2026,1,1,tzinfo=timezone.utc)
        p={"start":"20260101000000 +0000","stop":"20260102000000 +0000"}
        r=quality([p,p],now)
        self.assertEqual(r["coverage_pct"],100)
        self.assertEqual(r["duplicate_intervals"],1)
        self.assertTrue(r["current"])
    def test_gap(self):
        now=datetime(2026,1,1,tzinfo=timezone.utc)
        r=quality([{"start":"20260101010000 +0000","stop":"20260101120000 +0000"},{"start":"bad"}],now)
        self.assertEqual(r["largest_gap_minutes"],720)
        self.assertEqual(r["invalid"],1)
        self.assertFalse(r["current"])
