"""Evidence tables and Vietnamese report. All figures derive from retained rows."""
import re
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import findfont
from matplotlib.ft2font import FT2Font
from preprocess import ISSUE, has_issue, mask

# These evidence categories are not inferred BERTopic labels; counts are lexical mentions.
CATEGORIES=[
 ('Pin và sạc',r'\b(?:pin|sạc)\b','Thử nghiệm thời lượng pin và hướng dẫn chẩn đoán sạc.'),
 ('Cảm biến và điều hướng',r'\b(?:cảm biến|bản đồ|định vị|lạc|điều hướng)\b','Cung cấp hướng dẫn xử lý cảm biến và khôi phục bản đồ.'),
 ('Hiệu quả hút và lau',r'\b(?:hút|lau|sạch|bẩn)\b','Minh họa khả năng vệ sinh theo loại sàn và vết bẩn.'),
 ('Kết nối và ứng dụng',r'\b(?:app|wifi|wi-fi|kết nối|ứng dụng)\b','Hướng dẫn ghép nối và xử lý lỗi ứng dụng bằng tiếng Việt.'),
 ('Độ bền và sửa chữa',r'\b(?:hỏng|sửa|bảo hành|linh kiện|thay)\b','Làm rõ bảo hành, chi phí sửa và khả năng mua linh kiện.'),
 ('Tiếng ồn và mắc kẹt',r'\b(?:ồn|kẹt|vướng|ồn ào)\b','Nêu giới hạn vận hành và cách chuẩn bị không gian.'),
 ('Chi phí và lựa chọn sản phẩm',r'\b(?:giá|tiền|triệu|mua|chọn|nên)\b','Công bố tổng chi phí và bảng so sánh theo nhu cầu.'),
 ('Nước và vệ sinh trạm',r'\b(?:nước|trạm|giặt|rác|mùi)\b','Giải thích bảo trì trạm, bình nước và lịch vệ sinh.')]

def csv(df,path):
    df.to_csv(path,index=False,encoding='utf-8-sig')

def examples(group,n=2):
    return ' | '.join(group.text_masked.head(n).map(lambda s:mask(s).replace('\n',' ')[:500]))

def topic_tables(df,model):
    rows=[]
    for tid,g in df.groupby('topic_id',sort=True):
        words=[w for w,_ in (model.get_topic(int(tid)) or [])][:10]
        reps=model.get_representative_docs(int(tid)) or []
        if tid==-1: name='Khác / Chưa phân nhóm'
        else:
            # Evidence-driven candidate: score both cluster keywords and representative sentences.
            evidence=' '.join(words+reps)
            scored=[(len(re.findall(pattern,evidence,re.I)),label) for label,pattern,_ in CATEGORIES]
            best=max(scored)
            name=best[1] if best[0] else 'Trao đổi: '+' / '.join(words[:3]).replace('_',' ')
            keys=' '.join(words)
            if 'nước' in keys and ('vệ_sinh' in keys or 'giặt' in keys): name='Nước lau và vệ sinh trạm'
            elif 'qrevo' in keys and 'roborock' in keys: name='Lựa chọn dòng Roborock Qrevo'
            elif 'hơn' in keys and any(t in keys for t in ['t90','t50','x11']): name='So sánh mẫu máy và tính năng'
            elif 'robot' in keys and 'hút' in keys: name='Robot và máy lau hút cầm tay'
            elif 'giá' in keys and ('xin' in keys or 'xin giá' in evidence.lower()): name='Hỏi giá và trao đổi ngắn'
        rows.append(dict(topic_id=int(tid),topic_name_vi=name,needs_human_review=True,count=len(g),share_all_retained_pct=100*len(g)/len(df),top_keywords='; '.join(words),representative_examples= ' | '.join(mask(s)[:500] for s in reps[:2]) or examples(g)))
    summary=pd.DataFrame(rows).sort_values('count',ascending=False)
    names=summary.set_index('topic_id').topic_name_vi
    df['topic_name_vi']=df.topic_id.map(names)
    cross=[]
    for tid,g in df.groupby('topic_id'):
        for label in ['positive','neutral','negative']:
            count=int((g.sentiment_label==label).sum())
            cross.append(dict(topic_id=tid,topic_name_vi=names[tid],sentiment_label=label,count=count,pct_within_topic=100*count/len(g),pct_all_retained=100*count/len(df)))
    cross=pd.DataFrame(cross)
    refine_topic_names(df,summary,cross)
    return summary,cross

def refine_topic_names(df,summary,cross):
    """Propose specific names from the recorded keywords and representative text."""
    for idx,r in summary.iterrows():
        if r.topic_id==-1: continue
        keys=r.top_keywords; reps=r.representative_examples.lower()
        if keys.split(';')[0].strip()=='pin': name='Pin và chế độ vận hành'
        elif 'tầng' in keys and 'nhà' in keys: name='Sử dụng tại nhà và khoảng trống gầm'
        elif keys.startswith('x11') and 't90' in reps: name='So sánh X11 và T90'
        elif all(word in keys.split('; ') for word in ['mua','giá','bán']): name='Giá mua và nơi bán'
        else: continue
        summary.loc[idx,'topic_name_vi']=name
    names=summary.set_index('topic_id').topic_name_vi
    df['topic_name_vi']=df.topic_id.map(names)
    cross['topic_name_vi']=cross.topic_id.map(names)

PAIN_RULES=[
 ('Lỗi cảm biến hoặc bo mạch',r'(?:lỗi|hỏng|báo lỗi|bị).{0,35}(?:cảm biến|cảm ứng|main|bo mạch|mạch điều khiển)|(?:cảm biến|main).{0,20}(?:lỗi|hỏng)',None,'Dịch vụ: quy trình chẩn đoán, báo giá và xác nhận lỗi trước khi thay bo mạch.'),
 ('Hút nước bẩn, độ kín bình và khay giặt',r'(?:tắc|đọng|nghẹt|lỏng|khít|hở|không|ko).{0,70}(?:nước bẩn|nc bẩn|khay giặt|bình nước|gioăng)|(?:khay giặt|bình nước|nước bẩn).{0,70}(?:tắc|đọng|không|ko|hở|lỏng)',None,'Sản phẩm/dịch vụ: kiểm tra độ kín bình, đường hút nước và hướng dẫn vệ sinh khay.'),
 ('Mùi giẻ và nhu cầu giặt/vệ sinh bằng tay',r'hôi|tanh|giặt tay|tháo giẻ.{0,25}giặt',None,'Nội dung: lịch vệ sinh và cách xử lý mùi theo hướng dẫn hãng; không khuyến nghị hóa chất theo bình luận.'),
 ('Pin, khởi động và sạc',r'hết pin|hỏng pin|pin die|pin yếu|chai pin|hao pin|nhanh hết pin|không sạc|ko sạc|pin\b.{0,20}(?:không|ko)|sạc\b.{0,20}(?:lỗi|không|ko)',None,'Sản phẩm/nội dung: công bố thời lượng theo chế độ, hướng dẫn sạc và kiểm tra tiếp điểm.'),
 ('Chi phí sửa và thời gian/kết quả bảo hành',r'(?:bảo hành|bh|sửa|thay).{0,30}(?:\d+\s*(?:ngày|lần)|\d+(?:[.,]\d+)?\s*(?:tr|triệu))|bảo hành.{0,20}(?:không|hk|ko).{0,20}(?:khắc phục|được)',None,'Dịch vụ: báo giá minh bạch, thời hạn xử lý và cơ chế theo dõi bảo hành.'),
 ('Bê máy và trạm giữa các tầng',r'bê|cồng kềnh|nặng',r'tầng|bê|trạm','Sản phẩm/nội dung: tư vấn cấu hình theo số tầng, cân nhắc máy cầm tay và tổng chi phí.'),
 ('Gầm thấp, vật cản và dây điện',r'gầm|sofa|dây điện|bậc',r'thấp|chui|leo|kẹt|dây','Sản phẩm/nội dung: công bố chiều cao thực tế, khả năng vượt bậc và thử nghiệm vật cản.'),
 ('Khóa app và khó khăn cài đặt',r'khóa app|khoá app|app.{0,20}chưa kết nối|cài đặt.{0,25}(?:khó|vất|vật)|khó sử dụng',None,'Dịch vụ/nội dung: làm rõ phiên bản, khả năng kết nối và hướng dẫn cài đặt tiếng Việt.')]

def pain_evidence(df):
    rows=[]
    for label,pattern,second,opportunity in PAIN_RULES:
        pattern=r'\b(?:'+pattern+r')\b'
        match=df.text_for_topic.str.contains(pattern,case=False,regex=True)
        if second:
            second=r'\b(?:'+second+r')\b'
            match &= df.text_for_topic.str.contains(second,case=False,regex=True)
        g=df.loc[match]
        if not len(g): continue
        rows.append(dict(pain_point=label,candidate_comment_count=len(g),share_all_retained_pct=100*len(g)/len(df),topic_ids=', '.join(map(str,sorted(g.topic_id.unique()))),source_row_ids=', '.join(map(str,g.source_row_id)),masked_examples=examples(g),opportunity_hypothesis=opportunity,matching_rule=pattern,required_secondary_rule=second or ''))
    columns=['pain_point','candidate_comment_count','share_all_retained_pct','topic_ids','source_row_ids','masked_examples','opportunity_hypothesis','matching_rule','required_secondary_rule']
    return pd.DataFrame(rows,columns=columns).sort_values('candidate_comment_count',ascending=False)

def sentiment_dist(df):
    return pd.DataFrame([dict(sentiment_label=s,count=int((df.sentiment_label==s).sum()),percentage=100*(df.sentiment_label==s).mean()) for s in ['positive','neutral','negative']])

def sensitivity(df):
    rows=[]
    for scope,g in [('primary',df),('organic_only',df[df.commercial_label=='organic'])]:
        for sentiment in ['positive','neutral','negative']:
            count=int((g.sentiment_label==sentiment).sum())
            rows.append(dict(scope=scope,metric='sentiment',category=sentiment,count=count,denominator=len(g),percentage=100*count/len(g) if len(g) else np.nan))
        for tid in sorted(df.topic_id.unique()):
            count=int((g.topic_id==tid).sum())
            rows.append(dict(scope=scope,metric='topic_fixed_primary_clusters',category=str(tid),count=count,denominator=len(g),percentage=100*count/len(g) if len(g) else np.nan))
    return pd.DataFrame(rows)

def evidence_table(df):
    rows=[]
    for label,pattern,opportunity in CATEGORIES:
        g=df[df.text_for_topic.str.contains(pattern,case=False,regex=True)]
        pain=g.loc[g.text_for_topic.map(has_issue).astype(bool)]
        rows.append(dict(category=label,mention_count=len(g),issue_signal_count=len(pain),topic_ids=', '.join(map(str,sorted(g.topic_id.unique()))),issue_topic_ids=', '.join(map(str,sorted(pain.topic_id.unique()))),masked_examples=examples(g),issue_examples=examples(pain),opportunity_hypothesis=opportunity))
    return pd.DataFrame(rows)

def plots(df,summary,dist,cross,out):
    cmap=FT2Font(findfont('DejaVu Sans')).get_charmap()
    assert all(ord(c) in cmap for c in 'Tiếng Việt cảm biến hút bụi' if not c.isspace())
    plt.rcParams.update({'font.family':'DejaVu Sans','figure.facecolor':'white','axes.facecolor':'white','savefig.dpi':180})
    n=len(df)
    def save(fig,name):
        fig.tight_layout(); fig.savefig(out/name,dpi=180); plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,5)); names=['Tích cực','Trung tính','Tiêu cực']
    ax.bar(names,dist['count'],color=['#4b9b69','#97a3ad','#d86b63'])
    for i,r in enumerate(dist.itertuples()): ax.text(i,r.count,f'{r.count} ({r.percentage:.1f}%)',ha='center',va='bottom')
    ax.set_title(f'Phân bố cảm xúc dự đoán (n={n})'); ax.set_ylabel('Số bình luận'); ax.margins(y=.15); save(fig,'sentiment_distribution.png')
    fig,ax=plt.subplots(figsize=(8,5)); ax.hist(df.sentiment_score,bins=30,color='#537ca0'); ax.set_title(f'Điểm cảm xúc: P(tích cực) − P(tiêu cực), n={n}'); ax.set_xlabel('Điểm [-1, 1]'); ax.set_ylabel('Số bình luận'); save(fig,'sentiment_score_distribution.png')
    selected=summary[summary.topic_id!=-1].head(15)
    selected=pd.concat([selected,summary[summary.topic_id==-1]])
    fig,ax=plt.subplots(figsize=(12,max(5,len(selected)*.5)))
    labels=[f'{r.topic_id}: {r.topic_name_vi}' for r in selected.itertuples()]
    ax.barh(labels,selected['count'],color=['#9b9b9b' if t==-1 else '#537ca0' for t in selected.topic_id]); ax.invert_yaxis()
    for i,r in enumerate(selected.itertuples()): ax.text(r.count,i,f' {r.count} ({r.share_all_retained_pct:.1f}%)',va='center')
    ax.set_xlim(0,max(selected['count'])*1.3); ax.set_title(f'Chủ đề: tối đa 15 nhóm + chưa phân nhóm; mẫu số n={n}'); ax.set_xlabel('Số bình luận'); save(fig,'topic_bar_chart.png')
    negative=cross[cross.sentiment_label=='negative'].set_index('topic_id').reindex(summary.topic_id)
    fig,ax=plt.subplots(figsize=(8,max(4,len(negative)*.4)))
    im=ax.imshow(negative[['pct_within_topic']],vmin=0,vmax=100,cmap='Reds',aspect='auto'); ax.set_yticks(range(len(negative)),[f'{r.topic_id}: {r.topic_name_vi}' for r in summary.itertuples()]); ax.set_xticks([0],['Tỷ lệ tiêu cực trong chủ đề (%)'])
    for i,v in enumerate(negative.pct_within_topic): ax.text(0,i,f'{v:.1f}%',ha='center',va='center')
    fig.colorbar(im,ax=ax); ax.set_title(f'Cảm xúc dự đoán theo chủ đề (n={n})'); save(fig,'topic_sentiment_heatmap.png')

def report(df,audit,summary,dist,evidence,sens,metadata,out):
    n=len(df); lines=['# Phân tích bình luận Facebook về robot hút bụi','',
        '## Phạm vi và dữ liệu',f'Chỉ phân tích worksheet `comments`, cột `text`. Có {len(audit):,} dòng đầu vào; giữ lại {n:,} bình luận. Mỗi dòng là bình luận, không phải khách hàng duy nhất. Không có mã người dùng.',
        '','### Phễu lọc (các lý do loại trừ loại trừ lẫn nhau)']
    for reason,count in audit.cleaning_status.value_counts().items(): lines.append(f'- {reason}: {count:,}')
    lines+=['','Chính: organic + mixed_commercial có dấu hiệu vấn đề; loại quảng cáo thuần, uncertain, trùng và rỗng. Near-duplicate chưa được loại; chỉ trùng chính xác sau chuẩn hóa. Quy tắc thương mại là heuristic cần người kiểm tra.','',
        '## Cảm xúc dự đoán',f'Mẫu số: {n} bình luận giữ lại. Điểm = P(positive) − P(negative). Không phải khảo sát hài lòng.']
    for r in dist.itertuples(): lines.append(f'- {r.sentiment_label}: {r.count} ({r.percentage:.2f}%).')
    lines+=['','### Kiểm tra hành vi mô hình và trải nghiệm tích cực',
        'Mô hình cảm xúc huấn luyện trên 30.000 đánh giá thương mại điện tử; không phải mô hình đã được xác nhận cho nhóm Facebook này.']
    smoke=out/'model_smoke_predictions.csv'
    if smoke.exists():
        for r in pd.read_csv(smoke).itertuples(): lines.append(f'- Câu thử tự tạo (không thuộc mẫu dữ liệu): “{r.text}” → {r.sentiment_label}, độ tin cậy {r.sentiment_confidence:.3f}.')
    lines.append('Câu chẩn đoán có thể bị gán tiêu cực dù không thể hiện cảm xúc; độ tin cậy không đồng nghĩa độ chính xác.')
    for tid,g in df[df.sentiment_label=='positive'].groupby('topic_id'):
        if len(g)>=3:
            lines.append(f'- Topic {tid}: {len(g)} dự đoán tích cực; ví dụ đã che liên hệ: {examples(g)}. Đây là ví dụ mô hình gán tích cực, chưa phải đánh giá hài lòng được xác nhận.')
    lines+=['','## Chủ đề thảo luận','Tên chủ đề là nhãn gợi ý từ từ khóa và câu đại diện, cần người duyệt. Mẫu số gồm cả topic -1.']
    for r in summary.itertuples():
        lines += [f'### Chủ đề {r.topic_id}: {r.topic_name_vi}',f'{r.count} bình luận ({r.share_all_retained_pct:.2f}% toàn bộ mẫu giữ lại). Từ khóa: {r.top_keywords}.',f'Ví dụ: {r.representative_examples}','']
    pain=pain_evidence(df); csv(pain,out/'pain_point_evidence.csv')
    lines+=['## Vướng mắc cụ thể và cơ hội ưu tiên','Các số sau là bình luận ứng viên khớp quy tắc công khai trong pain_point_evidence.csv, có thể gồm câu hỏi, chẩn đoán hoặc lời khuyên; không phải số sự cố đã xác nhận, không phải tỷ lệ khách hàng bị lỗi. Các nhóm có thể chồng lấp. Ưu tiên thăm dò theo số đề cập, chưa đo mức nghiêm trọng hay hiệu quả kinh doanh.']
    for rank,r in enumerate(pain.itertuples(),start=1):
        lines += [f'### Ưu tiên {rank}: {r.pain_point}',f'{r.candidate_comment_count} bình luận ứng viên ({r.share_all_retained_pct:.2f}% trên {n}); topic {r.topic_ids}.',f'Ví dụ: {r.masked_examples}',f'Giả thuyết cơ hội: {r.opportunity_hypothesis}','']
    lines+=['## Phụ lục dấu hiệu theo nhóm tính năng','Các nhóm dưới đây đếm bằng biểu thức từ khóa công khai; có thể chồng lấp. “Dấu hiệu vấn đề” không đồng nghĩa cảm xúc tiêu cực. Không suy diễn nguyên nhân mua hàng.']
    supported=0
    for r in evidence.sort_values('issue_signal_count',ascending=False).itertuples():
        if not r.issue_signal_count: continue
        supported+=1
        lines += [f'### Ưu tiên {supported}: {r.category}',f'Đo lường: {r.issue_signal_count} bình luận có đồng thời từ khóa nhóm này và dấu hiệu vấn đề, trong {r.mention_count} lượt đề cập nhóm. Đây là đồng xuất hiện trong bình luận, không khẳng định lỗi thuộc về tính năng đó. Chủ đề liên quan đến dấu hiệu vấn đề: {r.issue_topic_ids}.',f'Ví dụ đã che liên hệ: {r.issue_examples}',f'Giả thuyết cơ hội (ưu tiên theo số đề cập vấn đề, chưa kiểm chứng): {r.opportunity_hypothesis}','']
    if supported<5: lines.append(f'Chỉ có {supported} nhóm vấn đề có bằng chứng theo quy tắc; không bịa thêm để đủ 5–10 nhóm.')
    lines+=['## Yếu tố được nhắc tới khi lựa chọn','Tần suất đề cập không chứng minh động cơ hay yếu tố gây ra quyết định mua.']
    for r in evidence.sort_values('mention_count',ascending=False).itertuples():
        if r.mention_count: lines += [f'- {r.category}: {r.mention_count} bình luận; topic {r.topic_ids}. Ví dụ: {r.masked_examples}']
    lines+=['','## Phân tích độ nhạy: chỉ organic','Giữ cố định topic của mô hình chính; không tái huấn luyện cụm, nên không đo độ ổn định khi tái huấn luyện.']
    for r in sens[(sens.scope=='organic_only') & (sens.metric=='sentiment')].itertuples(): lines.append(f'- {r.category}: {r.count}/{r.denominator} ({r.percentage:.2f}%).')
    queries=df[df.text_masked.str.contains(r'(?i)\bxin giá\b|giá bnhieu|giá bao nhiêu',regex=True)]
    wrong_candidates=queries[queries.sentiment_label=='negative']
    diagnostics=df[df.text_masked.str.contains(r'(?i)^lỗi (?:cảm biến|main|e7)',regex=True)]
    lines+=['','## Kiểm tra hành vi dự đoán — chưa có nhãn người',
        f'Trong {len(queries)} bình luận chứa “xin giá / giá bao nhiêu / giá bnhieu”, có {len(wrong_candidates)} bị mô hình gán negative. Đây là dấu hiệu cần duyệt, không phải đo độ chính xác bằng nhãn chuẩn.']
    for r in wrong_candidates.head(2).itertuples(): lines.append(f'- Dòng Excel {r.source_row_id}, topic {r.topic_id}: “{r.text_masked}” → {r.sentiment_label}, độ tin cậy {r.sentiment_confidence:.3f}.')
    lines.append(f'Có {len(diagnostics)} bình luận bắt đầu bằng chẩn đoán “lỗi cảm biến / main / E7”; không được mặc định coi chẩn đoán là bất mãn.')
    for r in diagnostics.head(2).itertuples(): lines.append(f'- Dòng Excel {r.source_row_id}, topic {r.topic_id}: “{r.text_masked}” → {r.sentiment_label}.')
    lines+=['Cụm lớn chứa trao đổi ngắn có thể trộn hỏi giá, chẩn đoán và phản hồi xã giao; không đồng nhất toàn bộ cụm với nhu cầu mua. Nhãn organic theo quy tắc không chứng minh tác giả là khách hàng; quảng cáo vẫn có thể lọt bộ lọc.',
        'Nên dùng chủ đề, câu trích và mẫu kiểm tra để thăm dò; không dùng tỷ lệ cảm xúc làm KPI hài lòng hay suy diễn quy mô thị trường.']
    lines+=['','## Giới hạn và yêu cầu kiểm tra',
      '- Mẫu nhóm Facebook không ngẫu nhiên; có quảng cáo và nội dung hỗn hợp. Không đại diện thị trường hay khách hàng duy nhất.',
      '- Mô hình tiền huấn luyện có lệch miền; mỉa mai, phủ định và chẩn đoán như “lỗi cảm biến” có thể bị hiểu sai. Không tuyên bố độ chính xác đã được xác nhận.',
      '- BERTopic/UMAP/HDBSCAN phụ thuộc tham số, seed và phiên bản. Chưa kiểm tra ổn định đa seed.',
      '- Tên chủ đề, nhãn thương mại và mẫu cảm xúc cần người kiểm tra. Các cột human_label để trống; chưa có xác nhận của người gán nhãn.',
      '- Xem sentiment_review_sample.csv để kiểm tra phủ định, chẩn đoán, nghi ngờ mỉa mai, nội dung thương mại hỗn hợp và độ tin cậy thấp.',
      '- Văn bản dài có thể bị cắt khi phân loại: '+str(metadata['parameters'].get('sentiment_truncated_count',0))+' bình luận.',
      '- Embedding cắt ở giới hạn mô hình: '+str(metadata['parameters'].get('embedding_truncated_count',0))+' bình luận. Từ ngữ phủ định lỗi phổ biến được loại khỏi quy tắc dấu hiệu vấn đề, nhưng quy tắc vẫn có thể sai.',
      '- Chi tiết mô hình, commit mô hình, phiên bản thư viện, thời gian và tham số có trong run_metadata.json.']
    (out/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
