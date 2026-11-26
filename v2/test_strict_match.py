import unittest
from v2.strict_match import audit

class StrictTests(unittest.TestCase):
    def test_candidates_not_approved(self):
        p=[{"channel_number":"1","channel_name":"ABC Philadelphia"}]
        c={"source":[{"id":"national","names":["ABC"],"future":20},{"id":"local","names":["ABC Philadelphia"],"future":20}]}
        self.assertEqual(audit(p,c,{})[0]["status"],"review_required")
        r={"ABC Philadelphia":[{"source":"source","id":"local","identity_evidence":"Fixture: verified WPVI"}]}
        self.assertEqual(audit(p,c,r)[0]["approved"],[("source","local")])
        c["source"][1]["future"]=0
        self.assertFalse(audit(p,c,r)[0]["approved"])
    def test_duplicate_id(self):
        p=[{"channel_number":"1","channel_name":"NBC East"}]
        c={"s":[{"id":"1","future":1,"names":["NBC East"]},{"id":"1","future":1,"names":["NBC West"]}]}
        r={"NBC East":[{"source":"s","id":"1","identity_evidence":"fixture"}]}
        self.assertFalse(audit(p,c,r)[0]["approved"])
