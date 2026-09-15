"""Select reproducible private listening queue; selection is not validation."""
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def main():
    data = pd.read_csv(ROOT / 'data/analytic.csv')
    rng = np.random.default_rng(20260915)
    random_ids = []
    for group in ['human', 'ai']:
        ids = sorted(data.loc[data.group.eq(group), 'call_id'])
        random_ids.extend(sorted(rng.choice(ids, 5, replace=False).tolist()))
    flagged = data.loc[data.needs_audio_review.eq(True), 'call_id'].tolist()
    queue = {'status': 'pending_independent_audio_review', 'seed': 20260915,
             'random_stratified': random_ids, 'flagged': flagged,
             'all_ids': sorted(set(random_ids + flagged))}
    target = ROOT / 'data/private/audit_queue.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(queue, indent=2), encoding='utf-8')
    print(f'Audit queue: {len(queue["all_ids"])} calls; listening NOT yet performed.')


if __name__ == '__main__':
    main()
