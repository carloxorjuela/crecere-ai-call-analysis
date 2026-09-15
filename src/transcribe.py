"""Resumable local ASR; originals and transcripts stay outside git."""
import argparse
import csv
from dataclasses import asdict
import json
import os
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault('HF_HOME', str(ROOT / '.cache' / 'huggingface'))
os.environ.setdefault('HF_HUB_DISABLE_SYMLINKS_WARNING', '1')
from faster_whisper import WhisperModel


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', default='large-v3-turbo')
    parser.add_argument('--limit', type=int, default=0)
    parser.add_argument('--threads', type=int, default=8)
    args = parser.parse_args()
    rows = list(csv.DictReader((ROOT / 'data/private/inventory.csv').open(encoding='utf-8')))
    # Alternate groups; shorter files first for the initial runtime/quality pilot.
    groups = {g: sorted([r for r in rows if r['group']==g], key=lambda r: float(r['duration_seconds'])) for g in ['human', 'ai']}
    rows = [r for pair in zip(groups['human'], groups['ai']) for r in pair]
    output = ROOT / 'data/private/transcripts' / args.model.replace('/', '_')
    output.mkdir(parents=True, exist_ok=True)
    pending = [r for r in rows if not (output / (r['call_id']+'.json')).exists()]
    if args.limit:
        pending = pending[:args.limit]
    if not pending:
        print('No pending recordings.', flush=True)
        return
    print(f'Loading {args.model}; pending={len(pending)}', flush=True)
    model = WhisperModel(args.model, device='cpu', compute_type='int8', cpu_threads=args.threads)
    for row in pending:
        start = time.monotonic()
        segments, info = model.transcribe(str(ROOT / row['source']), language='es', beam_size=5, vad_filter=True, condition_on_previous_text=False, word_timestamps=True)
        result = dict(call_id=row['call_id'], model=args.model, engine='faster-whisper', language='es', beam_size=5, vad_filter=True, condition_on_previous_text=False, source_sha256=row['sha256'], segments=[asdict(s) for s in segments])
        result['processing_seconds'] = round(time.monotonic()-start, 2)
        result['text'] = ' '.join(s['text'].strip() for s in result['segments'])
        target = output / (row['call_id']+'.json')
        temp = target.with_suffix('.tmp')
        temp.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        temp.replace(target)
        print(f"{row['call_id']}: audio={float(row['duration_seconds']):.1f}s processing={result['processing_seconds']}s segments={len(result['segments'])}", flush=True)


if __name__ == '__main__':
    main()
