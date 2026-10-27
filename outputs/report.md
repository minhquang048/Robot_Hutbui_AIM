# Báo cáo kiểm tra dữ liệu — phân tích chưa hoàn tất

Worksheet: comments. Dòng đầu vào: 1824. Thiếu text: 7.
Giữ lại theo quy tắc: 1114.

Các lý do loại trừ:
- uncertain: 335
- commercial: 188
- exact_duplicate: 180
- empty: 7

## Chặn thực thi
Pretrained model download/load failed: proxy/access denied (403); hosts=us.aws.cdn.hf.co. No sentiment scores or topics were fabricated. Check Hugging Face network access/cache.

Chưa có kết quả cảm xúc, BERTopic, biểu đồ hoặc kết luận kinh doanh. Không thay thế bằng điểm giả hay mô hình từ vựng.
cleaning_audit.csv và commercial_review_sample.csv là kết quả kiểm tra dữ liệu đã chạy; nhãn thương mại là heuristic, cần người duyệt.
Mẫu số là bình luận, không phải khách hàng duy nhất. Chỉ dùng comments; không dùng group_posts.
Cần mở quyền tải mô hình, chạy lại pipeline, kiểm tra các tổng và thực hiện duyệt mẫu trước khi sử dụng kết luận.
