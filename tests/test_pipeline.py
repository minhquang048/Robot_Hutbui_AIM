import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import pandas as pd
import pytest
from preprocess import normalize, mask, assert_private, commercial, audit_frame, stratified_sample, issue_content
from reporting import sentiment_dist,sensitivity,topic_tables

def test_mask_contacts_without_destroying_vietnamese_models_or_negation():
    text='Máy Roborock S7 không hút sạch 😢. Gọi 0912 345 678, +84 912-345-678; a.b@example.com @shop123 https://facebook.com/me'
    masked=mask(normalize(text))
    assert_private(masked)
    assert 'Roborock S7 không hút sạch 😢' in masked
    assert masked.count('[PHONE]')==2
    assert '[EMAIL]' in masked and '[HANDLE]' in masked and '[URL]' in masked

def test_normalization_null_and_canonical_equivalence():
    assert normalize(None)==''
    assert normalize('lỗi\u200b  &amp; pin!!!')=='lỗi & pin!!'

def test_multisignal_commercial_rules_keep_diagnostic_content():
    assert commercial('Lỗi cảm biến rồi')[0]=='organic'
    assert commercial('Giá Roborock S7 bao nhiêu, bảo hành thế nào?')[0]=='organic'
    assert commercial('Bên em nhận sửa robot, inbox zalo')[0]=='commercial'
    assert commercial('Máy lỗi cảm biến. Bên em nhận sửa, inbox zalo')[0]=='mixed_commercial'
    assert commercial('Cho mình xin báo giá')[0]=='uncertain'
    assert issue_content('Máy lỗi cảm biến. Bên em nhận sửa inbox zalo.')=='Máy lỗi cảm biến.'

def test_filtering_funnel_and_duplicates_do_not_double_count_exclusions():
    df=audit_frame([None,'   ','Lỗi cảm biến rồi','Lỗi  cảm biến rồi','Pin yếu','Bên em bán, inbox zalo','Báo giá nhé'])
    assert len(df)==7
    assert df.cleaning_status.value_counts().to_dict()=={'empty':2,'retained':2,'exact_duplicate':1,'commercial':1,'uncertain':1}
    assert df.source_row_id.tolist()==list(range(2,9))
    assert df.is_duplicate.sum()==1

def test_stratified_sample_reproducible_and_covers_rare_class():
    df=pd.DataFrame({'label':['a']*100+['b','c'],'value':range(102)})
    a=stratified_sample(df,'label',10,42)
    pd.testing.assert_frame_equal(a,stratified_sample(df,'label',10,42))
    assert len(a)==10 and set(a.label)=={'a','b','c'}

def test_aggregation_includes_outliers_and_sensitivity_denominators():
    class TopicModel:
        def get_topic(self,t): return [('pin',.5),('sạc',.3)]
        def get_representative_docs(self,t): return ['Máy không sạc được']
    df=pd.DataFrame({'topic_id':[-1,0,0],'commercial_label':['organic','organic','mixed_commercial'], 'sentiment_label':['neutral','negative','positive'],'text_masked':['Lỗi pin','Máy không sạc được','Pin mới']})
    summary,cross=topic_tables(df,TopicModel())
    assert summary['count'].sum()==cross['count'].sum()==3
    assert -1 in summary.topic_id.tolist()
    assert summary.loc[summary.topic_id==0,'topic_name_vi'].iloc[0]=='Pin và sạc'
    assert sentiment_dist(df)['count'].sum()==3
    sens=sensitivity(df)
    assert set(sens[sens.scope=='organic_only'].denominator)=={2}
    assert sens[(sens.scope=='organic_only')&(sens.metric=='sentiment')]['count'].sum()==2

def test_privacy_checker_rejects_unmasked_details():
    for text in ['Gọi 0912345678','mail a@example.com','@contact']:
        with pytest.raises(AssertionError): assert_private(text)

def test_mask_street_contact_and_bare_domain():
    masked=mask('Lỗi pin. Website nsnl.vn. Địa chỉ: Số 5 đường A, Hà Nội')
    assert 'Số 5' not in masked and 'nsnl.vn' not in masked
    assert 'Lỗi pin' in masked and '[ADDRESS]' in masked

def test_artifact_validation_rejects_inconsistent_results(tmp_path):
    """Fixture data tests reporting/validation only; never used as analysis output."""
    import json
    from reporting import csv,plots,report,evidence_table
    from run_nlp import validate
    class TopicModel:
        def get_topic(self,t): return [('pin',.5),('sạc',.3)]
        def get_representative_docs(self,t): return ['Máy không sạc được']
    audit=audit_frame(['Máy không sạc được','Lỗi cảm biến rồi','Hút sạch lắm'])
    df=audit.copy()
    df['topic_id']=[0,-1,1]; df['topic_probability']=[.8,0,.9]
    df['sentiment_label']=['negative','neutral','positive']
    df['sentiment_score']=[-.7,0,.7]; df['sentiment_confidence']=[.8,.8,.8]
    df['p_negative']=[.8,.1,.1]; df['p_neutral']=[.1,.8,.1]; df['p_positive']=[.1,.1,.8]
    summary,cross=topic_tables(df,TopicModel()); dist=sentiment_dist(df); sens=sensitivity(df)
    for table,name in [(df,'comment_level_results.csv'),(audit,'cleaning_audit.csv'),(audit,'commercial_review_sample.csv'),(summary,'topic_summary.csv'),(cross,'topic_sentiment_crosstab.csv'),(dist,'sentiment_distribution.csv')]: csv(table,tmp_path/name)
    plots(df,summary,dist,cross,tmp_path)
    report(df,audit,summary,dist,evidence_table(df),sens,{'parameters':{}},tmp_path)
    (tmp_path/'run_metadata.json').write_text(json.dumps({'status':'test_fixture_only'}))
    assert validate(tmp_path,3)['status']=='passed'
    cross.loc[0,'count']+=1; csv(cross,tmp_path/'topic_sentiment_crosstab.csv')
    with pytest.raises(AssertionError): validate(tmp_path,3)
