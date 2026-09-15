"""Duration comparison; separate from effectiveness or productive talk time."""
import csv
import json
from pathlib import Path
import numpy as np
from scipy.stats import permutation_test

ROOT = Path(__file__).resolve().parents[1]


def main():
    source = ROOT / 'data/analytic.csv'
    if not source.exists():
        source = ROOT / 'data/private/inventory.csv'
    rows = list(csv.DictReader(source.open(encoding='utf-8')))
    groups = {g: np.array([float(r['duration_seconds']) for r in rows if r['group']==g]) for g in ['human', 'ai']}
    rng = np.random.default_rng(20260914)
    human, ai = groups['human'], groups['ai']
    boot = np.median(rng.choice(ai, (20000, len(ai))), axis=1) - np.median(rng.choice(human, (20000, len(human))), axis=1)
    test = permutation_test((ai, human), lambda a,b: np.median(a)-np.median(b), n_resamples=19999, alternative='two-sided', rng=np.random.default_rng(20260914))
    result = {g: {'n':len(a), 'median_seconds':float(np.median(a)), 'mean_seconds':float(np.mean(a)), 'q25_seconds':float(np.quantile(a,.25)), 'q75_seconds':float(np.quantile(a,.75)), 'total_minutes':float(a.sum()/60)} for g,a in groups.items()}
    result['comparison'] = dict(estimand='median AI minus median human, seconds', difference_seconds=float(np.median(ai)-np.median(human)), bootstrap_95ci_seconds=np.quantile(boot,[.025,.975]).tolist(), permutation_pvalue=float(test.pvalue), bootstrap_resamples=20000, permutation_resamples=19999, seed=20260914, limitation='Recorded duration includes pauses and redactions; this is not productive talk time or cost per recovered payment.')
    output = ROOT / ('results/duration_analysis.json' if source.name=='analytic.csv' else 'data/private/duration_analysis.json')
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
