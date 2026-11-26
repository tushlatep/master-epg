import unittest
from datetime import datetime,timezone
import xml.etree.ElementTree as ET
from private_merge import merge

class MergeTests(unittest.TestCase):
    def setUp(self):
        self.now=datetime(2026,1,1,tzinfo=timezone.utc)
        self.root=ET.fromstring('<tv><channel id="a"><display-name>Station A</display-name></channel><programme channel="a" start="20260101000000 +0000" stop="20260102000000 +0000"><title>Test</title></programme></tv>')
        self.entry={'status':'verified','identity_evidence':'synthetic test only','channel_name':'Station A HD','sources':[{'source':'test','id':'a'}]}
    def test_exact(self):
        out=merge([self.entry],{'test':self.root},self.now)
        self.assertEqual(out.find('programme').get('channel'),'Station A HD')
    def test_unverified(self):
        self.entry['status']='candidate'
        with self.assertRaises(ValueError): merge([self.entry],{'test':self.root},self.now)
    def test_wrong_id(self):
        self.entry['sources'][0]['id']='wrong'
        with self.assertRaises(ValueError): merge([self.entry],{'test':self.root},self.now)
    def test_gap(self):
        self.root.find('programme').set('stop','20260101120000 +0000')
        with self.assertRaises(ValueError): merge([self.entry],{'test':self.root},self.now)
