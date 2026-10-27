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
STREET = re.compile(r'(?i)\b(?:số\s+\d+[\w/.-]*\s*[, ]\s*(?:ngách|ngõ|đường|phố|hẻm|ấp|tổ)|(?:ngách|ngõ|hẻm|đường|phố)\s+\d+)\b[^;\n]*')
CONTACT = re.compile(r'(?i)\b(?:zalo|hotline|sđt|sdt|điện thoại|liên hệ)\b')
CTA = re.compile(r'(?i)\b(?:inbox|ib|inb|ibx|nhắn tin|báo giá|chốt đơn|giảm giá|ưu đãi|đặt hàng|nhận sửa|chuyên sửa|bên em|bên mình|shop em|em bán|mình bán|cần mua|cần bán|pass lại|cần pass|pass con|mình pass|em pass|e pass)\b')
OFFER = re.compile(r'(?i)\b(?:nhận sửa|chuyên sửa|bên em|bên mình|shop em|em bán|mình bán|cần bán|pass lại|cần pass|pass con|mình pass|em pass|e pass|giảm giá|ưu đãi|chốt đơn|đặt hàng)\b')
INVENTORY = re.compile(r'(?i)\b(?:sẵn hàng|sẵn giá|e sẵn|em sẵn|mình sẵn|nhà em|bên e|xả kho|thanh lý|mình có hàng|em có hàng|hàng sẵn|sẵn kho|còn hàng|new qt|nguyên seal)\b')
INCENTIVE = re.compile(r'(?i)\b(?:sale|sa-le|giá tốt|giá cực tốt|giá sốc|giá siêu|giá ưu đãi|ưu đãi|giảm giá|áp mã|hoàn \d+|rẻ chưa|khuyến mãi|chốt|link chính hãng)\b')
DELIVERY = re.compile(r'(?i)\b(?:ship|freeship|ship_cod|cod|giao hàng|giao lắp|miễn phí toàn quốc|miễn phí vận chuyển|thu tiền tại nhà|xem máy tại)\b')
SELLER = re.compile(r'(?i)\b(?:em có|e có|bên em|bên e|bên mình|nhà em|mình bán|em bán|shop em|nhận sửa|chuyên sửa)\b')
PRICE = re.compile(r'(?i)\b\d+(?:[.,]\d+)?\s*(?:tr|triệu|k|đồng|xxx|x)\b')
ISSUE = re.compile(r'(?i)\b(?:lỗi|hỏng|không\s+(?:chạy|sạc|hút|lau|lên|nhận|kết nối)|chưa\s+(?:chạy|sạc)|yếu|kẹt|ồn|báo đỏ|mất bản đồ|hao pin|chai pin|rò nước|không sạch)\b')

def has_issue(text):
    s=re.sub(r'(?i)\b(?:không|ko|k|chưa|ít)\s+(?:(?:bị|có|gặp|thấy)\s+){0,2}(?:lỗi(?:\s+lầm)?|hỏng|kẹt|ồn)\b',' ',text)
    s=re.sub(r'(?i)\b(?:chống|tránh)\s+(?:kẹt|ồn)\b|\bgặp lỗi gì\b',' ',s)
    s=re.sub(r'(?i)\blỗi lớn cũng có\b|\bnhận sửa\s+(?:(?:hết|mọi|các)\s+)?lỗi\b',' ',s)
    if SELLER.search(text):
        s=re.sub(r'(?i)\b(?:bảo hành|đổi mới)\s+máy lỗi\b',' ',s)
    return bool(ISSUE.search(s))

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
    s = STREET.sub('[ADDRESS]', s)
    s = EMAIL.sub('[EMAIL]', s)
    s = PHONE.sub('[PHONE]', s)
    s = URL.sub('[URL]', s)
    return HANDLE.sub('[HANDLE]', s)

def commercial(text):
    contact = bool(EMAIL.search(text) or PHONE.search(text) or HANDLE.search(text) or CONTACT.search(text))
    cta = bool(CTA.search(text)); offer = bool(OFFER.search(text)); issue = has_issue(text)
    inventory=bool(INVENTORY.search(text)); incentive=bool(INCENTIVE.search(text)); delivery=bool(DELIVERY.search(text)); seller=bool(SELLER.search(text)); price=bool(PRICE.search(text))
    reasons = [name for name, flag in [('contact', contact), ('call_to_action', cta), ('offer', offer), ('inventory',inventory), ('incentive',incentive), ('delivery',delivery), ('seller_voice',seller), ('price',price), ('issue', issue)] if flag]
    promotional = ((contact and (cta or offer or inventory or seller)) or (offer and cta)
                   or (inventory and (incentive or delivery or price or cta))
                   or (seller and (incentive or delivery or price)) or (incentive and delivery)
                   or ('[URL]' in text and (incentive or inventory or offer or seller)))
    if promotional:
        label = 'mixed_commercial' if issue else 'commercial'
    elif cta or contact or offer or inventory or delivery:
        label = 'uncertain'
    else:
        label = 'organic'
    return label, ';'.join(reasons) or 'no_commercial_signal'

def issue_content(text):
    # Remove separable sales-only sentences, never remove a sentence carrying an issue.
    chunks = re.split(r'(?<=[.!?;])\s+|[\n\r]+', text)
    kept = [s for s in chunks if has_issue(s) or not (CTA.search(s) or CONTACT.search(s) or OFFER.search(s) or INVENTORY.search(s) or INCENTIVE.search(s) or DELIVERY.search(s))]
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
    if EMAIL.search(str(text)) or PHONE.search(str(text)) or HANDLE.search(str(text)) or ADDRESS.search(str(text)) or STREET.search(str(text)):
        raise AssertionError('Unmasked contact details detected in export')
