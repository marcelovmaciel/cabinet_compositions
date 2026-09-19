"""Small fixtures and one fresh reconstruction shared by the scientific suite."""
import atexit
from functools import cache
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
ROOT=Path(__file__).resolve().parents[1]
INPUTS=ROOT/'data/normalized'
SOURCE=ROOT/'data/source'
sys.path.insert(0,str(ROOT/'src'))
sys.path.insert(0,str(ROOT/'scripts'))
import build as b
import build_release as pipeline
from paths import BUILD, build_path
BUILD.mkdir(exist_ok=True)
tempfile.tempdir=str(BUILD)

@cache
def reconstruction():
    temporary=tempfile.TemporaryDirectory(prefix='tests-',dir=BUILD)
    atexit.register(temporary.cleanup)
    return pipeline.reconstruct(Path(temporary.name)/'reconstructed')

def sv(person='p',sid='s',start='2020-01-01',end='2020-02-01',capacity='titular'):
 return dict(person_id=person,service_id=sid,start_inclusive=start,end_exclusive=end,capacity=capacity,decision_ids='',evidence_ids='')
def af(person='p',state='PARTY',party='PR',alts=()):
 return dict(person_id=person,affiliation_id='a'+person,start_inclusive='2020-01-01',end_exclusive='2020-02-01',state=state,party_id=party,date_status='',alternatives=json.dumps(alts),decision_ids='',evidence_ids='')
