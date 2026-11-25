import unittest, tempfile, os, gzip
from pathlib import Path
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
import xml.etree.ElementTree as ET
from build_epg import build

class BuildTests(unittest.TestCase):
    def test_merge_alias_logo_and_failure(self):
        now=datetime.now(timezone.utc)
        start=now.strftime("%Y%m%d%H%M%S %z")
        stop=(now+timedelta(hours=2)).strftime("%Y%m%d%H%M%S %z")
        p=f'<programme channel="WPVI.us" start="{start}" stop="{stop}"><title>Test news</title></programme>'
        a=f'<tv><channel id="WPVI.us"><display-name>WPVI</display-name></channel>{p}{p}</tv>'
        b='<tv><channel id="WPVI.us"><display-name>WPVI</display-name><icon src="https://example.com/logo.png"/></channel></tv>'
        cfg={"sources":[{"url":u,"enabled":True,"redistribution_confirmed":True} for u in ["a","b"]],"aliases":{"WPVI.us":["ABC PHILADELPHIA 4K"]}}
        old=os.getcwd()
        with tempfile.TemporaryDirectory() as d:
            try:
                os.chdir(d)
                with patch("build_epg.fetch",side_effect=[a.encode(),b.encode()]): build(cfg)
                path=Path("output/master-epg.xml.gz")
                original=path.read_bytes()
                tree=ET.fromstring(gzip.decompress(original))
                self.assertEqual(len(tree.findall("programme")),1)
                self.assertIsNotNone(tree.find("channel/icon"))
                self.assertIn("ABC PHILADELPHIA 4K",[n.text for n in tree.findall("channel/display-name")])
                with patch("build_epg.fetch",side_effect=OSError("offline")):
                    with self.assertRaises(RuntimeError): build(cfg)
                self.assertEqual(path.read_bytes(),original)
            finally: os.chdir(old)

if __name__=="__main__": unittest.main()
