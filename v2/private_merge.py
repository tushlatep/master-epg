"""Private XMLTV merger. Use only independently verified registry entries."""
import copy,gzip,json,os,sys,tempfile
from pathlib import Path
from datetime import datetime,timezone
import xml.etree.ElementTree as ET
from schedule_quality import quality

def merge(registry, sources, now=None):
    now=now or datetime.now(timezone.utc)
    out=ET.Element('tv')
    used=set()
    for entry in registry:
        if entry.get('status')!='verified' or not entry.get('identity_evidence'):
            raise ValueError('Unverified registry entry')
        target=entry['channel_name']
        if target in used: raise ValueError('Duplicate target')
        used.add(target)
        for candidate in entry['sources']:
            root=sources.get(candidate['source'])
            if root is None: continue
            sid=candidate['id']
            channels=[c for c in root.findall('channel') if c.get('id')==sid]
            if len(channels)!=1: continue
            programmes=[p for p in root.findall('programme') if p.get('channel')==sid]
            q=quality([p.attrib for p in programmes],now)
            if q['coverage_pct']!=100 or not q['current'] or q['overlap_minutes'] or q['invalid'] or q['duplicate_intervals']: continue
            c=copy.deepcopy(channels[0]); c.set('id',target)
            for n in list(c.findall('display-name')): c.remove(n)
            ET.SubElement(c,'display-name').text=target
            out.append(c)
            for p in programmes:
                p=copy.deepcopy(p); p.set('channel',target); out.append(p)
            break
        else: raise ValueError('No qualifying exact source for '+target)
    if not used: raise ValueError('Empty registry')
    return out

def main():
    registry=json.loads(Path(sys.argv[1]).read_text())
    paths=json.loads(Path(sys.argv[2]).read_text())
    sources={}
    for key,path in paths.items():
        data=Path(path).read_bytes()
        sources[key]=ET.fromstring(gzip.decompress(data) if data.startswith(b'\x1f\x8b') else data)
        if sources[key].tag!='tv': raise ValueError('Not XMLTV')
    root=merge(registry,sources)
    dest=Path(sys.argv[3])
    with tempfile.NamedTemporaryFile(dir=dest.parent,delete=False) as f:
        temp=f.name
        f.write(gzip.compress(ET.tostring(root,encoding='utf-8',xml_declaration=True)))
    os.replace(temp,dest)

if __name__=='__main__': main()
