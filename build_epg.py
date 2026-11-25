import gzip, json, re, sys, urllib.request, xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter

def fetch(url):
    with urllib.request.urlopen(url, timeout=90) as r:
        data=r.read(150_000_001)
    if len(data)>150_000_000: raise ValueError("Source too large")
    return gzip.decompress(data) if data.startswith(b'\x1f\x8b') else data

def norm(s):
    return re.sub(r'[^a-z0-9]+','',re.sub(r'\b(4k|uhd|fhd|hd)\b','',s.lower()))

def build(config):
    root=ET.Element("tv", {"generator-info-name":"Master EPG"})
    channels={}; programmes={}; errors=[]
    for source in config["sources"]:
        if not source.get("enabled") or not source.get("redistribution_confirmed"): continue
        try:
            tree=ET.fromstring(fetch(source["url"]))
            if tree.tag!="tv": raise ValueError("Not XMLTV")
            for c in tree.findall("channel"):
                cid=c.get("id")
                if not cid: continue
                if cid not in channels: channels[cid]=c
                elif channels[cid].find("icon") is None and c.find("icon") is not None:
                    channels[cid].append(c.find("icon"))
            for p in tree.findall("programme"):
                cid=p.get("channel")
                if cid and cid not in programmes: programmes[cid]=[]
            grouped={}
            for p in tree.findall("programme"):
                grouped.setdefault(p.get("channel"),[]).append(p)
            for cid, items in grouped.items():
                if not programmes.get(cid): programmes[cid]=items
        except Exception as e: errors.append(str(e))
    if errors: raise RuntimeError("Source failure; retain previous output: "+str(errors))
    logos={}
    for entry in config.get("logos",[]):
        if entry.get("redistribution_confirmed"):
            for item in json.loads(fetch(entry["url"])):
                cid=item.get("channel"); url=item.get("url","")
                if cid and url.startswith("https://"): logos.setdefault(cid,url)
    aliases=config.get("aliases",{})
    now=datetime.now(timezone.utc)
    future=0; count=0
    for cid,c in channels.items():
        if c.find("icon") is None and cid in logos: ET.SubElement(c,"icon",src=logos[cid])
        existing={n.text for n in c.findall("display-name")}
        for name in aliases.get(cid,[]):
            if name not in existing: ET.SubElement(c,"display-name").text=name
        root.append(c)
    for cid,items in programmes.items():
        if cid not in channels: continue
        seen=set()
        for p in items:
            key=(p.get("start"),p.get("stop"),p.findtext("title"))
            if key in seen: continue
            seen.add(key)
            try:
                stop=datetime.strptime(p.get("stop",""),"%Y%m%d%H%M%S %z")
                if stop>now: future+=1
            except ValueError: continue
            root.append(p); count+=1
    if len(channels)<config.get("min_channels",1) or future<1: raise ValueError("Insufficient current guide data")
    out=Path("output"); out.mkdir(exist_ok=True)
    data=ET.tostring(root,encoding="utf-8",xml_declaration=True)
    ET.fromstring(data)
    tmp=out/"master-epg.xml.gz.tmp"; tmp.write_bytes(gzip.compress(data)); tmp.replace(out/"master-epg.xml.gz")
    (out/"report.json").write_text(json.dumps({"channels":len(channels),"channels_with_icons":sum(c.find("icon") is not None for c in channels.values()),"programmes":count,"future_programmes":future,"updated":now.isoformat()},indent=2))
if __name__=="__main__":
    build(json.loads(Path("config.json").read_text()))
