"""Sensitivity pass using a lower speech-detection threshold on the same ASR model."""
import argparse
import csv
from dataclasses import asdict
import json
from pathlib import Path
import time
from transcribe import ROOT, WhisperModel


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('ids',nargs='*')
    parser.add_argument('--threads',type=int,default=4)
    args=parser.parse_args()
    inventory=list(csv.DictReader((ROOT/'data/private/inventory.csv').open(encoding='utf-8')))
    out=ROOT/'data/private/transcripts/sensitive'
    out.mkdir(parents=True,exist_ok=True)
    model=WhisperModel('large-v3-turbo',device='cpu',compute_type='int8',cpu_threads=args.threads)
    for row in inventory:
        cid=row['call_id']
        if args.ids and cid not in args.ids:
            continue
        target=out/(cid+'.json')
        if target.exists():
            continue
        start=time.monotonic()
        segments,info=model.transcribe(str(ROOT/row['source']),language='es',vad_filter=True,vad_parameters={'threshold':0.15,'min_silence_duration_ms':1000,'speech_pad_ms':400},condition_on_previous_text=False,beam_size=5)
        result={'call_id':cid,'model':'large-v3-turbo','vad_filter':True,'vad_threshold':0.15,'segments':[asdict(s) for s in segments]}
        result['text']=' '.join(s['text'].strip() for s in result['segments'])
        result['processing_seconds']=round(time.monotonic()-start,2)
        target.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        print(cid,result['processing_seconds'],flush=True)


if __name__=='__main__':
    main()
