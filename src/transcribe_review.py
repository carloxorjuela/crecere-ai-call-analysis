"""ASR sensitivity check without VAD for specified uncertain recordings."""
import argparse
import csv
from dataclasses import asdict
import json
from pathlib import Path
import time
from transcribe import ROOT, WhisperModel


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('ids',nargs='+')
    args=parser.parse_args()
    inventory={r['call_id']:r for r in csv.DictReader((ROOT/'data/private/inventory.csv').open(encoding='utf-8'))}
    out=ROOT/'data/private/transcripts/no_vad'
    out.mkdir(parents=True,exist_ok=True)
    model=WhisperModel('large-v3-turbo',device='cpu',compute_type='int8',cpu_threads=2)
    for cid in args.ids:
        target=out/(cid+'.json')
        if target.exists():
            continue
        start=time.monotonic()
        segments,info=model.transcribe(str(ROOT/inventory[cid]['source']),language='es',vad_filter=False,condition_on_previous_text=False,beam_size=5)
        result={'call_id':cid,'model':'large-v3-turbo','vad_filter':False,'segments':[asdict(s) for s in segments]}
        result['text']=' '.join(s['text'].strip() for s in result['segments'])
        result['processing_seconds']=round(time.monotonic()-start,2)
        target.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        print(cid,result['processing_seconds'],flush=True)


if __name__=='__main__':
    main()
