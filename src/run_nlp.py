#!/usr/bin/env python3
"""One-command, fail-closed Vietnamese comments analysis."""
import os
os.environ.setdefault('HF_HOME','/workspace/.cache/huggingface')
os.environ.setdefault('HF_HUB_DISABLE_XET','1')
os.environ.setdefault('XDG_CACHE_HOME','/workspace/.cache')
os.environ.setdefault('MPLCONFIGDIR','/workspace/.cache/matplotlib')
os.environ.setdefault('NUMBA_CACHE_DIR','/workspace/.cache/numba')
os.environ.setdefault('OMP_NUM_THREADS','2')
import argparse
from datetime import datetime,timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import random
import sys
import time
import traceback
import numpy as np
import pandas as pd
from preprocess import audit_frame, stratified_sample, assert_private
from reporting import csv, sentiment_dist, topic_tables, sensitivity, evidence_table, plots, report

REQUIRED=['cleaning_audit.csv','commercial_review_sample.csv','comment_level_results.csv','sentiment_distribution.csv','sentiment_distribution.png','sentiment_score_distribution.png','topic_summary.csv','topic_bar_chart.png','topic_sentiment_crosstab.csv','topic_sentiment_heatmap.png','report.md','run_metadata.json']

def arguments():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path); p.add_argument('--sheet',default='comments',choices=['comments'])
    p.add_argument('--output',type=Path,default=Path('outputs')); p.add_argument('--seed',type=int,default=42)
    p.add_argument('--min-chars',type=int,default=1); p.add_argument('--batch-size',type=int,default=16)
    p.add_argument('--sentiment-model',default='wonrax/phobert-base-vietnamese-sentiment')
    p.add_argument('--embedding-model',default='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
    p.add_argument('--sentiment-revision'); p.add_argument('--embedding-revision')
    p.add_argument('--overwrite',action='store_true',help='Replace outputs of a prior run (source workbook is never modified).')
    return p.parse_args()

def discover(path):
    if path:
        if not path.is_file(): raise FileNotFoundError(path)
        return path.resolve()
    matches=list(Path(__file__).resolve().parents[1].rglob('robothutbui_facebookscrape.xlsx'))
    if len(matches)!=1: raise ValueError(f'Expected one matching workbook, found {len(matches)}; specify --input.')
    return matches[0]

def validate(out,n):
    from PIL import Image
    dist=pd.read_csv(out/'sentiment_distribution.csv')
    topics=pd.read_csv(out/'topic_summary.csv')
    cross=pd.read_csv(out/'topic_sentiment_crosstab.csv')
    comments=pd.read_csv(out/'comment_level_results.csv')
    assert len(comments)==n and comments.source_row_id.is_unique
    assert int(dist['count'].sum())==int(topics['count'].sum())==int(cross['count'].sum())==n
    assert abs(dist.percentage.sum()-100)<1e-6
    assert abs(topics.share_all_retained_pct.sum()-100)<1e-6
    assert comments.sentiment_score.between(-1,1).all()
    assert np.allclose(comments[['p_positive','p_neutral','p_negative']].sum(axis=1),1,atol=1e-5)
    assert np.allclose(comments.sentiment_score,comments.p_positive-comments.p_negative,atol=1e-6)
    assert not comments[['topic_id','topic_name_vi','sentiment_label']].isna().any().any()
    for tid,g in comments.groupby('topic_id'):
        assert int(topics.loc[topics.topic_id==tid,'count'].iloc[0])==len(g)
        assert int(cross.loc[cross.topic_id==tid,'count'].sum())==len(g)
        for label,group in g.groupby('sentiment_label'):
            assert int(cross.loc[(cross.topic_id==tid)&(cross.sentiment_label==label),'count'].iloc[0])==len(group)
    for filename in REQUIRED:
        assert (out/filename).is_file() and (out/filename).stat().st_size>0,filename
    for path in out.glob('*.csv'):
        assert path.read_bytes().startswith(b'\xef\xbb\xbf'),path.name
        table=pd.read_csv(path)
        assert 'text_raw' not in table.columns
        for column in table.select_dtypes(include='object'):
            for value in table[column].dropna(): assert_private(value)
    assert_private((out/'report.md').read_text())
    for path in out.glob('*.png'):
        with Image.open(path) as image:
            assert image.width>100 and image.height>100
            assert image.info.get('dpi',(0,0))[0]>=159
            image.verify()
    return {'status':'passed','retained_count':n,'checks':['required artifacts','sum/denominator consistency','per-topic crosstab consistency','probability bounds and score formula','UTF-8 BOM CSV','masked exported contacts','PNG integrity and resolution']}

def main(args):
    start=time.monotonic(); out=args.output.resolve(); out.mkdir(parents=True,exist_ok=True)
    if args.min_chars<1 or args.batch_size<1: raise ValueError('min-chars and batch-size must be positive')
    if any(out.iterdir()):
        if not args.overwrite: raise FileExistsError('Output directory is not empty. Select a new directory or explicitly use --overwrite.')
        known=set(REQUIRED+['sentiment_review_sample.csv','sensitivity_results.csv','business_evidence.csv','pain_point_evidence.csv','model_smoke_predictions.csv','sentiment_model_card.md','embedding_model_card.md','validation.json','failure.txt','.incomplete'])
        unknown={p.name for p in out.iterdir()}-known
        if unknown: raise FileExistsError('Refusing to remove unrelated output files: '+str(sorted(unknown)))
        for p in out.iterdir(): p.unlink()
    (out/'.incomplete').write_text('Run is incomplete until validation succeeds.\n')
    source=discover(args.input); digest=hashlib.sha256(source.read_bytes()).hexdigest()
    book=pd.ExcelFile(source)
    if args.sheet not in book.sheet_names: raise ValueError('Required worksheet comments does not exist')
    raw=pd.read_excel(book,sheet_name=args.sheet)
    if 'text' not in raw: raise ValueError('Required column text does not exist')
    metadata={'status':'running','started_at_utc':datetime.now(timezone.utc).isoformat(),'input_path':str(source),'input_sha256':digest,'sheet':args.sheet,'columns':list(raw.columns),'original_rows':len(raw),'null_text_rows':int(raw.text.isna().sum()),'seed':args.seed,'python':sys.version,'platform':platform.platform(),'warnings':['No human labels supplied; review samples are pending.','Facebook non-random sample, commercial contamination, model domain shift and sarcasm.','Topic labels are evidence-based candidates requiring human review.'],'parameters':{'min_chars':args.min_chars,'batch_size':args.batch_size,'near_duplicate_removal':False},'models':{},'versions':{p:importlib.metadata.version(p) for p in ['torch','numpy','pandas','openpyxl','matplotlib','transformers','sentence-transformers','bertopic','umap-learn','hdbscan','underthesea','scikit-learn']}}
    try:
        metadata['stage_status']={'audit':'running','models':'unrun','sentiment':'unrun','topics':'unrun','report':'unrun','validation':'unrun'}
        random.seed(args.seed); np.random.seed(args.seed)
        audit=audit_frame(raw.text,args.min_chars)
        csv(audit,out/'cleaning_audit.csv')
        review=stratified_sample(audit,'commercial_label',min(80,len(audit)),args.seed)
        review['human_commercial_label']=''; review['human_notes']=''; csv(review,out/'commercial_review_sample.csv')
        df=audit[audit.cleaning_status=='retained'].copy().reset_index(drop=True)
        metadata.update(retained_rows=len(df),exclusion_counts={k:int(v) for k,v in audit.cleaning_status.value_counts().items() if k!='retained'},commercial_label_counts={k:int(v) for k,v in audit.commercial_label.value_counts().items()},exact_duplicate_flags=int(audit.is_duplicate.sum()))
        metadata['parameters']['primary_scope']='organic + issue-bearing mixed_commercial; exclude uncertain, commercial, empty and exact normalized duplicates'
        metadata['stage_status']['audit']='completed'
        for file in ['cleaning_audit.csv','commercial_review_sample.csv']:
            for column in pd.read_csv(out/file).select_dtypes('object'):
                for value in pd.read_csv(out/file)[column].dropna(): assert_private(value)
        print('Audit:',json.dumps({k:metadata[k] for k in ['original_rows','null_text_rows','retained_rows','exclusion_counts']},ensure_ascii=False),flush=True)
        if len(df)<6: raise ValueError('Insufficient retained corpus')
        from models import load_models,infer_sentiment,cluster
        import torch
        torch.manual_seed(args.seed); torch.set_num_threads(2); torch.use_deterministic_algorithms(True)
        metadata['stage_status']['models']='running'
        tok,classifier,embedder,mapping,info=load_models(args,out)
        metadata['stage_status']['models']='completed'
        print('Loaded and verified explicit model labels:', mapping, flush=True)
        for key,model in info.items(): (out/(key+'_model_card.md')).write_text(model.pop('model_card'),encoding='utf-8')
        metadata['models']=info
        smoke=['Máy hút rất sạch, tôi rất hài lòng.','Máy hỏng liên tục, tôi rất thất vọng.','Lỗi cảm biến rồi.','Máy không tốt như mong đợi.','Máy không bị lỗi, chạy ổn.']
        smoke_predictions,_=infer_sentiment(smoke,tok,classifier,mapping,args.batch_size)
        csv(pd.concat([pd.DataFrame({'text':smoke}),pd.DataFrame(smoke_predictions)],axis=1),out/'model_smoke_predictions.csv')
        if any(not np.isfinite(r['sentiment_score']) for r in smoke_predictions): raise ValueError('Nonfinite model smoke inference')
        metadata['stage_status']['sentiment']='running'
        predictions,params=infer_sentiment(df.text_for_sentiment.tolist(),tok,classifier,mapping,args.batch_size)
        metadata['stage_status']['sentiment']='completed'
        metadata['parameters'].update(params)
        df=pd.concat([df,pd.DataFrame(predictions)],axis=1)
        metadata['stage_status']['topics']='running'
        model,topics,probabilities,params=cluster(df.text_for_topic.tolist(),embedder,args.seed,args.batch_size)
        metadata['stage_status']['topics']='completed'
        metadata['parameters'].update(params)
        df['topic_id']=topics; df['topic_probability']=probabilities
        metadata['parameters']['topic_probability_definition']='HDBSCAN membership strength, not calibrated posterior; outlier is topic -1'
        summary,cross=topic_tables(df,model); dist=sentiment_dist(df); sens=sensitivity(df); evidence=evidence_table(df)
        review=df.copy()
        review['review_stratum']=np.select([review.commercial_label.eq('mixed_commercial'),review.sentiment_confidence.lt(.6),review.text_masked.str.contains(r'không|chưa|chẳng',case=False),review.text_masked.str.contains(r'lỗi|cảm biến|pin',case=False),review.text_masked.str.contains(r'haha|:v|quá tốt|tuyệt vời',case=False)],['mixed_commercial','uncertain_model','negation','diagnostic','possible_sarcasm'],default=review.sentiment_label)
        review=stratified_sample(review,'review_stratum',min(100,len(review)),args.seed)
        review['human_sentiment_label']=''; review['human_notes']=''
        for table,filename in [(df,'comment_level_results.csv'),(summary,'topic_summary.csv'),(cross,'topic_sentiment_crosstab.csv'),(dist,'sentiment_distribution.csv'),(sens,'sensitivity_results.csv'),(evidence,'business_evidence.csv'),(review,'sentiment_review_sample.csv')]: csv(table,out/filename)
        plots(df,summary,dist,cross,out)
        metadata['topic_count_excluding_outliers']=int((summary.topic_id!=-1).sum())
        metadata['outlier_count']=int((df.topic_id==-1).sum())
        if metadata['topic_count_excluding_outliers']<2: metadata['warnings'].append('Fewer than two non-outlier topics; robust clustering not established.')
        metadata['manual_review']={'status':'pending_human_labels','sample_size':len(review),'automatic_smoke_examples':len(smoke)}
        report(df,audit,summary,dist,evidence,sens,metadata,out)
        metadata['stage_status']['report']='completed_pending_human_review'
        metadata['status']='completed_pending_human_review'; metadata['runtime_seconds']=time.monotonic()-start
        (out/'run_metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
        checks=validate(out,len(df)); (out/'validation.json').write_text(json.dumps(checks,indent=2))
        metadata['stage_status']['validation']='passed'
        (out/'run_metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
        (out/'.incomplete').unlink()
        assert hashlib.sha256(source.read_bytes()).hexdigest()==digest,'Input workbook changed'
        print('Validated retained comments:',len(df),'topics (including -1):',len(summary),flush=True)
    except Exception as e:
        for stage,status in metadata.get('stage_status',{}).items():
            if status=='running': metadata['stage_status'][stage]='failed'
        if hasattr(e,'model_info'): metadata['models']=e.model_info
        if not (out/'report.md').exists():
            counts=metadata.get('exclusion_counts',{})
            partial=['# Báo cáo kiểm tra dữ liệu — phân tích chưa hoàn tất','',
                f'Worksheet: comments. Dòng đầu vào: {len(raw)}. Thiếu text: {metadata["null_text_rows"]}.',
                f'Giữ lại theo quy tắc: {metadata.get("retained_rows",0)}.',
                '', 'Các lý do loại trừ:']
            partial += [f'- {reason}: {count}' for reason,count in counts.items()]
            partial += ['', '## Chặn thực thi',str(e),'',
                'Chưa có kết quả cảm xúc, BERTopic, biểu đồ hoặc kết luận kinh doanh. Không thay thế bằng điểm giả hay mô hình từ vựng.',
                'cleaning_audit.csv và commercial_review_sample.csv là kết quả kiểm tra dữ liệu đã chạy; nhãn thương mại là heuristic, cần người duyệt.',
                'Mẫu số là bình luận, không phải khách hàng duy nhất. Chỉ dùng comments; không dùng group_posts.',
                'Cần mở quyền tải mô hình, chạy lại pipeline, kiểm tra các tổng và thực hiện duyệt mẫu trước khi sử dụng kết luận.']
            (out/'report.md').write_text('\n'.join(partial)+'\n',encoding='utf-8')
        metadata.update(status='failed',runtime_seconds=time.monotonic()-start,error_type=type(e).__name__,error=str(e),incomplete_deliverables=[f for f in REQUIRED if f!='run_metadata.json' and (not (out/f).exists() or (f=='report.md' and metadata['stage_status']['report']=='unrun'))])
        (out/'run_metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
        (out/'failure.txt').write_text(type(e).__name__+': '+str(e)+'\n',encoding='utf-8')
        print('FAILED:',type(e).__name__,str(e),file=sys.stderr,flush=True)
        raise
    finally:
        for path in sorted(out.iterdir()): print(str(path),flush=True)

if __name__=='__main__':
    main(arguments())
