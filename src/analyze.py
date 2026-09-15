"""Reproducible comparisons from a reviewed, de-identified call table."""
import argparse
import json
from pathlib import Path
from statistics import NormalDist
import numpy as np
import pandas as pd
from scipy.stats import fisher_exact

ROOT = Path(__file__).resolve().parents[1]
BINARY = ['target_contact', 'evaluable', 'zero_discount_phrase', 'binary_answer_prompt', 'legal_terms', 'generic_doubt_response', 'dated_promise', 'explicit_promise', 'amount_agreed', 'next_step_agreed', 'closure_recap', 'objection', 'relevant_response', 'alternative_offered', 'prior_agreement', 'customer_speech']
PRIMARY = 'dated_promise'
# Comparisons not registered in docs/analysis_plan.md: one Holm family, still exploratory.
EXPLORATORY = ['target_contact', 'objection', 'alternative_offered', 'amount_agreed', 'next_step_agreed', 'closure_recap',
               'zero_discount_phrase', 'binary_answer_prompt', 'legal_terms', 'generic_doubt_response']


def wilson(k, n):
    if n == 0:
        return [None, None]
    z = NormalDist().inv_cdf(.975)
    p = k/n
    center = (p+z*z/(2*n))/(1+z*z/n)
    half = z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/(1+z*z/n)
    return [max(0., float(center-half)), min(1., float(center+half))]


def holm(pvalues):
    """Holm step-down adjusted p-values for a {name: p} family."""
    adjusted, running_max = {}, 0.
    for rank, key in enumerate(sorted(pvalues, key=pvalues.get)):
        running_max = max(running_max, min(1., (len(pvalues)-rank)*pvalues[key]))
        adjusted[key] = running_max
    return adjusted


def binary_comparison(frame, field):
    values = {}
    for group in ['human', 'ai']:
        group_rows = frame[frame.group.eq(group)]
        observed = group_rows[field].dropna()
        if not observed.isin([0,1]).all():
            raise ValueError(f'Invalid binary values for {field}')
        k, n = int(observed.sum()), len(observed)
        values[group] = dict(events=k, n=n, unknown_or_na=len(group_rows)-n, rate=k/n if n else None, wilson_95ci=wilson(k,n))
    h, a = values['human'], values['ai']
    if h['n'] and a['n']:
        delta = a['rate']-h['rate']
        # Newcombe independent-proportions score interval (unpooled Wilson).
        lower = delta-np.sqrt((a['rate']-a['wilson_95ci'][0])**2+(h['wilson_95ci'][1]-h['rate'])**2)
        upper = delta+np.sqrt((a['wilson_95ci'][1]-a['rate'])**2+(h['rate']-h['wilson_95ci'][0])**2)
        values['comparison'] = dict(difference_pp=100*delta, newcombe_95ci_pp=[float(100*lower), float(100*upper)], fisher_two_sided_p=float(fisher_exact([[a['events'],a['n']-a['events']],[h['events'],h['n']-h['events']]]).pvalue))
    return values


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, default=ROOT/'data/analytic.csv')
    args = parser.parse_args()
    frame = pd.read_csv(args.input)
    if frame.call_id.duplicated().any():
        raise ValueError('Duplicate call IDs')
    if set(frame.group) != {'human','ai'}:
        raise ValueError('Expected both groups')
    results = {'n_by_group': frame.groupby('group').size().to_dict(), 'metrics': {}}
    for field in BINARY:
        if field not in frame:
            continue
        subset = frame[frame.objection.eq(1)] if field=='relevant_response' else frame
        results['metrics'][field] = binary_comparison(subset,field)
    results['purpose_counts'] = pd.crosstab(frame.purpose,frame.group).to_dict()
    results['outcome_counts'] = pd.crosstab(frame.outcome,frame.group).to_dict()
    results['principal_sensitivity'] = {}
    for g in ['human','ai']:
        s=frame.loc[frame.group.eq(g),PRIMARY]
        results['principal_sensitivity'][g] = {'all_unknown_negative_rate':float(s.fillna(0).mean()), 'all_unknown_positive_rate':float(s.fillna(1).mean()), 'unknown':int(s.isna().sum())}
    results['within_purpose_exploratory'] = {p: binary_comparison(s,PRIMARY) for p,s in frame.groupby('purpose')}
    h=results['principal_sensitivity']['human']; a=results['principal_sensitivity']['ai']
    results['principal_difference_missing_bounds_pp']=[100*(a['all_unknown_negative_rate']-h['all_unknown_positive_rate']),100*(a['all_unknown_positive_rate']-h['all_unknown_negative_rate'])]
    duration_path=ROOT/'results/duration_analysis.json'
    response=results['metrics'].get('relevant_response',{}).get('comparison',{})
    if duration_path.exists() and response:
        duration=json.loads(duration_path.read_text(encoding='utf-8'))
        results['secondary_holm_pvalues']=holm({'duration':duration['comparison']['permutation_pvalue'],'relevant_response':response['fisher_two_sided_p']})
    results['exploratory_holm_pvalues']=holm({k: results['metrics'][k]['comparison']['fisher_two_sided_p'] for k in EXPLORATORY if k in results['metrics']})
    results['interpretation'] = 'Associations in a selected observational sample. No causal attribution, no realized payment measurement. Secondary/exploratory p-values are not confirmatory.'
    out = ROOT/'results'
    out.mkdir(exist_ok=True)
    (out/'analysis.json').write_text(json.dumps(results,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
    print(json.dumps(results,indent=2,ensure_ascii=False,allow_nan=False))


if __name__ == '__main__':
    main()
