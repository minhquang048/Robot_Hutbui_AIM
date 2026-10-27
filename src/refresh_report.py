#!/usr/bin/env python3
"""Rebuild labels, charts and report from a completed, verified real model run."""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import pandas as pd
from run_nlp import validate
from reporting import report,plots,refine_topic_names,csv

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,default=Path('outputs'))
a=p.parse_args(); out=a.output.resolve()
m=json.loads((out/'run_metadata.json').read_text())
assert m['status']=='completed_pending_human_review','Cannot refresh a failed/incomplete model run'
assert not (out/'.incomplete').exists()
validate(out,m['retained_rows'])
load=lambda name: pd.read_csv(out/(name+'.csv'))
df=load('comment_level_results'); summary=load('topic_summary'); cross=load('topic_sentiment_crosstab'); dist=load('sentiment_distribution')
refine_topic_names(df,summary,cross)
for table,name in [(df,'comment_level_results'),(summary,'topic_summary'),(cross,'topic_sentiment_crosstab')]: csv(table,out/(name+'.csv'))
review=load('sentiment_review_sample'); review['topic_name_vi']=review.topic_id.map(summary.set_index('topic_id').topic_name_vi); csv(review,out/'sentiment_review_sample.csv')
plots(df,summary,dist,cross,out)
report(df,load('cleaning_audit'),summary,dist,load('business_evidence'),load('sensitivity_results'),m,out)
m['report_refreshed_at_utc']=datetime.now(timezone.utc).isoformat()
(out/'run_metadata.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
checks=validate(out,m['retained_rows'])
(out/'validation.json').write_text(json.dumps(checks,indent=2))
print('Labels, charts and report rebuilt and verified:',out/'report.md')
