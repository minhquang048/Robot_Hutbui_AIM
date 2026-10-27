"""Auditable Vietnamese normalization, commercial rules and contact masking."""
import html
import re
import unicodedata
import pandas as pd

EMAIL = re.compile(r'(?i)(?<![\w.+-])[\w.+-]+\s*@\s*[\w.-]+\.[a-z]{2,}')
# Conservative: also redact long numeric identifiers; preserve ordinary prices/model codes.
PHONE = re.compile(r'(?<!\w)(?:\+?84|0)(?:[\s.()\-]*\d){8,10}(?!\d)|(?<!\w)\+?\d(?:[\s.()\-]*\d){8,14}(?!\w)')
HANDLE = re.compile(r'(?<!\w)@[\w.\-]+', re.UNICODE)
URL = re.compile(r'(?i)(?:https?://|www\.)\S+|(?<![@\w])(?:[a-z0-9-]+\.)+(?:com|vn|net|org|io)(?:/\S*)?\b')
ADDRESS = re.compile(r'(?i)(?:địa\s*chỉ|đ/c|đc\s*:)\s*[:\-]?\s*[^;\n]+')
CONTACT = re.compile(r'(?i)\b(?:zalo|hotline|sđt|sdt|điện thoại|liên hệ)\b')
CTA = re.compile(r'(?i)\b(?:inbox|ib|nhắn tin|báo giá|chốt đơn|giảm giá|ưu đãi|đặt hàng|nhận sửa|chuyên sửa|bên em|bên mình|shop em|em bán|mình bán|cần mua|cần bán|pass lại)\b')
OFFER = re.compile(r'(?i)\b(?:nhận sửa|chuyên sửa|bên em|bên mình|shop em|em bán|mình bán|cần bán|pass lại|giảm giá|ưu đãi|chốt đơn|đặt hàng)\b')
ISSUE = re.compile(r'(?i)\b(?:lỗi|hỏng|không\s+(?:chạy|sạc|hút|lau|lên|nhận|kết nối)|chưa\s+(?:chạy|sạc)|yếu|kẹt|ồn|báo đỏ|mất bản đồ|hao pin|chai pin|rò nước|không sạch)\b')

def normalize(value):
    if pd.isna(value):
        return ''
    s = unicodedata.normalize('NFC', html.unescape(str(value)))
    s = re.sub(r'[\u200b-\u200f\u202a-\u202e\u2060\ufeff]', '', s)
    s = re.sub(r'<[^>]*>', ' ', s)
    s = URL.sub(' [URL] ', s)
    s = re.sub(r'([!?.,])\1{2,}', r'\1\1', s)
    return re.sub(r'\s+', ' ', s).strip()

def mask(text):
    s = ADDRESS.sub('[ADDRESS]', str(text))
    s = EMAIL.sub('[EMAIL]', s)
    s = PHONE.sub('[PHONE]', s)
    s = URL.sub('[URL]', s)
    return HANDLE.sub('[HANDLE]', s)

def commercial(text):
    contact = bool(EMAIL.search(text) or PHONE.search(text) or HANDLE.search(text) or CONTACT.search(text))
    cta = bool(CTA.search(text)); offer = bool(OFFER.search(text)); issue = bool(ISSUE.search(text))
    reasons = [name for name, flag in [('contact', contact), ('call_to_action', cta), ('offer', offer), ('issue', issue)] if flag]
    promotional = (contact and cta) or (offer and cta)
    if promotional:
        label = 'mixed_commercial' if issue else 'commercial'
    elif cta or contact or offer:
        label = 'uncertain'
    else:
        label = 'organic'
    return label, ';'.join(reasons) or 'no_commercial_signal'

def issue_content(text):
    # Remove separable sales-only sentences, never remove a sentence carrying an issue.
    chunks = re.split(r'(?<=[.!?;])\s+|[\n\r]+', text)
    kept = [s for s in chunks if ISSUE.search(s) or not (CTA.search(s) or CONTACT.search(s) or OFFER.search(s))]
    return ' '.join(kept).strip() or text

def audit_frame(raw, min_chars=1):
    records=[]; seen=set()
    for i, value in enumerate(raw, start=2):
        normalized = normalize(value)
        duplicate = bool(normalized and normalized in seen)
        if normalized:
            seen.add(normalized)
        label, reason = commercial(normalized)
        status = ('empty' if not normalized else 'exact_duplicate' if duplicate else
                  'below_min_chars' if len(normalized) < min_chars else
                  'commercial' if label == 'commercial' else 'uncertain' if label == 'uncertain' else 'retained')
        content = issue_content(normalized) if label == 'mixed_commercial' else normalized
        records.append(dict(source_row_id=i, text_masked=mask(normalized),
                            text_for_sentiment=mask(content), text_for_topic=mask(content),
                            commercial_label=label, commercial_reason=reason,
                            is_duplicate=duplicate, cleaning_status=status))
    return pd.DataFrame(records)

def stratified_sample(df, column, n, seed):
    if df.empty:
        return df.copy()
    # Round-robin across shuffled strata ensures rare labels enter the sample.
    groups=[g.sample(frac=1,random_state=seed) for _, g in df.groupby(column,dropna=False,sort=True)]
    order=[]
    for i in range(max(map(len,groups))):
        for group in groups:
            if i < len(group): order.append(group.index[i])
            if len(order) >= min(n,len(df)): return df.loc[order].copy()
    return df.loc[order].copy()

def assert_private(text):
    if EMAIL.search(str(text)) or PHONE.search(str(text)) or HANDLE.search(str(text)) or ADDRESS.search(str(text)):
        raise AssertionError('Unmasked contact details detected in export')
