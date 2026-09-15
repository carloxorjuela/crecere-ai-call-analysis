"""Exploratory, auditable phrase flags; not sentiment or legal classification."""
import json
import re
import unicodedata
from pathlib import Path
from collections import Counter

ROOT=Path(__file__).resolve().parents[1]
PATTERNS={
    'binary_answer_prompt':r'\bsi (?:o |o un )no\b',
    'legal_terms':r'\b(?:embargos?|judicializaciones?|judicial|juridic[oa]|proceso legal)\b',
    'zero_discount_phrase':r'descuento (?:del? )?(?:0\s*%|cero por ciento)',
    'generic_doubt_response':r'permitame atender sus dudas',
}


def normalize(text):
    return ''.join(c for c in unicodedata.normalize('NFKD',text.lower()) if not unicodedata.combining(c))


def main():
    rows=[]
    for path in sorted((ROOT/'data/private/transcripts/large-v3-turbo').glob('*.json')):
        data=json.loads(path.read_text(encoding='utf-8'))
        text=normalize(data['text'])
        supplement=ROOT/'data/private/transcripts/sensitive'/path.name
        if supplement.exists():
            text+=' '+normalize(json.loads(supplement.read_text(encoding='utf-8'))['text'])
        row={'call_id':data['call_id']}
        for name,pattern in PATTERNS.items():
            row[name]=int(bool(re.search(pattern,text)))
        rows.append(row)
    output=ROOT/'data/private/lexical_features.json'
    output.write_text(json.dumps(rows,indent=2),encoding='utf-8')
    print(json.dumps({'n':len(rows),'flag_counts':{g:dict(Counter({key:sum(r[key] for r in rows if r['call_id'].startswith(g)) for key in PATTERNS})) for g in ['human','ai']}},indent=2))


if __name__=='__main__':
    main()
