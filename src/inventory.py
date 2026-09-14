"""Inventory WAV recordings without exposing original filenames publicly."""
from pathlib import Path
import csv
import hashlib
import json
import wave
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]


def main():
    private = ROOT / 'data' / 'private'
    private.mkdir(parents=True, exist_ok=True)
    rows = []
    for group, folder in [('human', 'audios_humanos_censurados'), ('ai', 'audios_ia_censurados')]:
        for index, path in enumerate(sorted((ROOT / 'audios_prueba_data_analyst' / folder).glob('*.wav')), 1):
            row = dict(call_id=f'{group}_{index:03d}', group=group, source=str(path.relative_to(ROOT)), bytes=path.stat().st_size)
            row['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
            try:
                with wave.open(str(path), 'rb') as wav:
                    row.update(duration_seconds=wav.getnframes()/wav.getframerate(), sample_rate=wav.getframerate(), channels=wav.getnchannels(), sample_width=wav.getsampwidth(), error='')
            except (wave.Error, EOFError) as exc:
                row.update(duration_seconds=None, sample_rate=None, channels=None, sample_width=None, error=str(exc))
            rows.append(row)
    with (private / 'inventory.csv').open('w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    hashes = defaultdict(list)
    for row in rows:
        hashes[row['sha256']].append(row['call_id'])
    summary = {}
    for group in ['human', 'ai']:
        subset = [r for r in rows if r['group'] == group]
        durations = sorted(r['duration_seconds'] for r in subset if r['duration_seconds'] is not None)
        summary[group] = dict(count=len(subset), minutes=sum(durations)/60, minimum_seconds=min(durations, default=None), maximum_seconds=max(durations, default=None), errors=sum(bool(r['error']) for r in subset))
    summary['duplicate_sets'] = [ids for ids in hashes.values() if len(ids)>1]
    (private / 'inventory_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
