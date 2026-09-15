"""Convert documented transcript coding into a de-identified analytical table."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BINARY = ['evaluable','customer_speech','target_contact','explicit_promise','dated_promise','amount_agreed','prior_agreement','objection','relevant_response','alternative_offered','next_step_agreed','closure_recap']


def main():
    inventory = {r['call_id']:r for r in csv.DictReader((ROOT/'data/private/inventory.csv').open(encoding='utf-8'))}
    coded = {}
    for path in sorted((ROOT/'data/private').glob('annotations_batch*.json')):
        batch = json.loads(path.read_text(encoding='utf-8'))
        for values in batch['rows']:
            if len(values)!=len(batch['fields']):
                raise ValueError(f'Wrong row length in {path.name}: {values[0]}')
            row = dict(zip(batch['fields'],values))
            cid=row['call_id']
            if cid in coded or cid not in inventory:
                raise ValueError(f'Duplicate or invalid ID: {cid}')
            for key in BINARY:
                if row[key] not in (None,0,1):
                    raise ValueError(f'Invalid binary code {cid}/{key}')
            if row['dated_promise']==1 and row['explicit_promise']!=1:
                raise ValueError(f'Dated promise requires explicit acceptance: {cid}')
            if row['objection']!=1 and row['relevant_response'] is not None:
                raise ValueError(f'Response has no observable objection: {cid}')
            row['group']=inventory[cid]['group']
            row['duration_seconds']=float(inventory[cid]['duration_seconds'])
            row['review_status']='transcript_reviewed'
            coded[cid]=row
    overrides_path=ROOT/'data/private/review_overrides.json'
    if overrides_path.exists():
        for change in json.loads(overrides_path.read_text(encoding='utf-8')):
            cid=change['call_id']
            if cid not in coded or not change.get('reason'):
                raise ValueError('Override requires existing ID and documented reason')
            coded[cid].update(change['changes'])
    for cid,row in coded.items():
        for key in BINARY:
            if row[key] not in (None,0,1):
                raise ValueError(f'Invalid reviewed code {cid}/{key}')
        if row['dated_promise']==1 and row['explicit_promise']!=1:
            raise ValueError(f'Reviewed dated promise requires acceptance: {cid}')
    # Public evaluability is defined by the primary outcome, not a global filter.
    for row in coded.values():
        row['evaluable']=int(row['dated_promise'] is not None)
    lexical_path=ROOT/'data/private/lexical_features.json'
    lexical_fields=[]
    if lexical_path.exists():
        lexical=json.loads(lexical_path.read_text(encoding='utf-8'))
        lexical_fields=[k for k in lexical[0] if k!='call_id'] if lexical else []
        for entry in lexical:
            if entry['call_id'] in coded:
                coded[entry['call_id']].update(entry)
    missing=sorted(set(inventory)-set(coded))
    output=ROOT/'data/private/analytic_working.csv' if missing else ROOT/'data/analytic.csv'
    fields=['call_id','group','duration_seconds']+BINARY+['purpose','outcome','objection_type','review_status','needs_audio_review']+lexical_fields
    with output.open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore')
        writer.writeheader()
        for cid in sorted(coded):
            row=coded[cid].copy()
            row['objection_type']='|'.join(row['objection_type'])
            writer.writerow(row)
    print(json.dumps({'coded':len(coded),'missing':missing,'output':str(output.relative_to(ROOT))},indent=2))


if __name__=='__main__':
    main()
