#!/usr/bin/env python3
"""Recheck existing run artifacts; --audit-only never claims full validation."""
import argparse
import hashlib
import json
from pathlib import Path
import pandas as pd
from preprocess import assert_private
from run_nlp import validate

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=Path('outputs'))
    parser.add_argument('--audit-only',action='store_true')
    args=parser.parse_args(); out=args.output.resolve()
    meta=json.loads((out/'run_metadata.json').read_text())
    audit=pd.read_csv(out/'cleaning_audit.csv')
    sample=pd.read_csv(out/'commercial_review_sample.csv')
    assert len(audit)==meta['original_rows']
    assert len(audit[audit.cleaning_status=='retained'])==meta['retained_rows']
    assert audit.source_row_id.is_unique and set(sample.source_row_id)<=set(audit.source_row_id)
    assert len(sample)<=80
    assert sum(meta['exclusion_counts'].values())+meta['retained_rows']==meta['original_rows']
    assert hashlib.sha256(Path(meta['input_path']).read_bytes()).hexdigest()==meta['input_sha256']
    for path in out.glob('*.csv'):
        assert path.read_bytes().startswith(b'\xef\xbb\xbf')
        frame=pd.read_csv(path)
        assert 'text_raw' not in frame.columns
        for col in frame.select_dtypes('object'):
            for text in frame[col].dropna(): assert_private(text)
    if args.audit_only:
        print(f'AUDIT ONLY PASSED: {len(audit)} rows, {meta["retained_rows"]} retained; review sample {len(sample)}. Full analysis status: {meta["status"]}')
    else:
        assert meta['status']=='completed_pending_human_review', 'Full run is incomplete'
        assert not (out/'.incomplete').exists(), 'Incomplete marker present'
        print(json.dumps(validate(out,meta['retained_rows']),ensure_ascii=False))

if __name__=='__main__': main()
