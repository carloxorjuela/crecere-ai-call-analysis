"""Print selected private transcripts with segment evidence IDs for review."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('ids', nargs='*')
parser.add_argument('--model', default='large-v3-turbo')
parser.add_argument('--list', action='store_true')
args = parser.parse_args()
folder = ROOT / 'data/private/transcripts' / args.model
files = sorted(folder.glob('*.json'))
if args.list:
    print(' '.join(f.stem for f in files))
else:
    for file in files:
        if args.ids and file.stem not in args.ids:
            continue
        data = json.loads(file.read_text(encoding='utf-8'))
        print('\n###', data['call_id'])
        for seg in data['segments']:
            print(f"[{seg['id']} {seg['start']:.1f}-{seg['end']:.1f}] {seg['text'].strip()}")
