# Phân tích bình luận Facebook về robot hút bụi

## Phạm vi và dữ liệu
Chỉ phân tích worksheet `comments`, cột `text`. Có 1,824 dòng đầu vào; giữ lại 932 bình luận. Mỗi dòng là bình luận, không phải khách hàng duy nhất. Không có mã người dùng.

### Phễu lọc (các lý do loại trừ loại trừ lẫn nhau)
- retained: 932
- commercial: 384
- uncertain: 321
- exact_duplicate: 180
- empty: 7

Chính: organic + mixed_commercial có dấu hiệu vấn đề; loại quảng cáo thuần, uncertain, trùng và rỗng. Near-duplicate chưa được loại; chỉ trùng chính xác sau chuẩn hóa. Quy tắc thương mại là heuristic cần người kiểm tra.

## Cảm xúc dự đoán
Mẫu số: 932 bình luận giữ lại. Điểm = P(positive) − P(negative). Không phải khảo sát hài lòng.
- positive: 366 (39.27%).
- neutral: 345 (37.02%).
- negative: 221 (23.71%).

### Kiểm tra hành vi mô hình và trải nghiệm tích cực
Mô hình cảm xúc huấn luyện trên 30.000 đánh giá thương mại điện tử; không phải mô hình đã được xác nhận cho nhóm Facebook này.
- Câu thử tự tạo (không thuộc mẫu dữ liệu): “Máy hút rất sạch, tôi rất hài lòng.” → positive, độ tin cậy 0.993.
- Câu thử tự tạo (không thuộc mẫu dữ liệu): “Máy hỏng liên tục, tôi rất thất vọng.” → negative, độ tin cậy 0.988.
- Câu thử tự tạo (không thuộc mẫu dữ liệu): “Lỗi cảm biến rồi.” → negative, độ tin cậy 0.979.
- Câu thử tự tạo (không thuộc mẫu dữ liệu): “Máy không tốt như mong đợi.” → negative, độ tin cậy 0.976.
- Câu thử tự tạo (không thuộc mẫu dữ liệu): “Máy không bị lỗi, chạy ổn.” → positive, độ tin cậy 0.965.
Câu chẩn đoán có thể bị gán tiêu cực dù không thể hiện cảm xúc; độ tin cậy không đồng nghĩa độ chính xác.
- Topic -1: 59 dự đoán tích cực; ví dụ đã che liên hệ: Dùng thích ạ, lực hút 25k ổn, có tự giặt giẻ, tự nâng giẻ, không có xoè giẻ vs giặt nước nóng thì phải. Mà nhà nhu cầu cơ bản thì vậy là ổn r | Roborocks s7 max unltra giá 16tr bao lắp đặt vận chuyên tận nơi bảo hành 24 tháng chính hãng ạ. Đây là ví dụ mô hình gán tích cực, chưa phải đánh giá hài lòng được xác nhận.
- Topic 0: 93 dự đoán tích cực; ví dụ đã che liên hệ: M sẵn nhé b | Rất OK a. Đây là ví dụ mô hình gán tích cực, chưa phải đánh giá hài lòng được xác nhận.
- Topic 1: 66 dự đoán tích cực; ví dụ đã che liên hệ: Có ai đang quan tâm đến sản phẩm này ko, ae bị thu hút bởi điều gì | lên shopee í mua bạn. Mình cũng mua trên đó. Đây là ví dụ mô hình gán tích cực, chưa phải đánh giá hài lòng được xác nhận.
- Topic 2: 21 dự đoán tích cực; ví dụ đã che liên hệ: Bà mua dung dịch nước rửa kính oto về pha . Một chai pha sài cả năm ko hết ý là tui sài bộ cấp xả ngày lau 2 lần đó. Vừa sạch vừa bóng. Tui dùng cả năm nay bữa tháo ra thay cái quạt hút cái bình nước sáng bóng. | con này nhà mình dùng thấy bền vs lau sạch mức tương đối, cũng tự giặt giẻ ok đó bác. hợp lau nhà hàng ngày không quá bẩn b ạ. Đây là ví dụ mô hình gán tích cực, chưa phải đánh giá hài lòng được xác nhận.
- Topic 3: 26 dự đoán tích cực; ví dụ đã che liên hệ: Dock sạc để sát tường thế kia robot về đc mới lạ | Robot hút bụi lau nhà Roborock Qrevo S Pro 9tr2. Hàng đmxanh giao cài đặt tại nhà ạ.. Đây là ví dụ mô hình gán tích cực, chưa phải đánh giá hài lòng được xác nhận.
- Topic 4: 39 dự đoán tích cực; ví dụ đã che liên hệ: Thái Lưu Quang Hải Phòng vó bác này ở 266B Trần Nguyên Hãn. Hỗ trợ nhiệt tình cả trước và sau bán. Mình mua của bác ấy mấy con rồi. Từ con ecovacs T5 đời đầu. Hôm trước mới lên đời con T90 xong | Đang dùng T20e omni gần 2 năm r trộm vía chưa bị gì. Con này đời sau ngon hơn nhiều. Đây là ví dụ mô hình gán tích cực, chưa phải đánh giá hài lòng được xác nhận.
- Topic 5: 38 dự đoán tích cực; ví dụ đã che liên hệ: 10tr lấy Qrevo S Pro của Roborock dùng rất ổn định luôn ạ | Qrevo S Pro ngon bác ạ! [URL]. Đây là ví dụ mô hình gán tích cực, chưa phải đánh giá hài lòng được xác nhận.
- Topic 7: 16 dự đoán tích cực; ví dụ đã che liên hệ: em đang có con dreame x50 utral màu trắng, mới nguyên hộp chính hãng, giá tầm 18tr ạ | E co s7 steam giá 8.5tr tặng nồi cơm cuckoo hơn 1tr Giao hà nội Còn các tỉnh khác e tặng 5 ấm siêu tốc ạ. Đây là ví dụ mô hình gán tích cực, chưa phải đánh giá hài lòng được xác nhận.
- Topic 8: 4 dự đoán tích cực; ví dụ đã che liên hệ: Nhà m đang dùng con này khá là ổn mà. | Em ở hải phòng nhé. Đây là ví dụ mô hình gán tích cực, chưa phải đánh giá hài lòng được xác nhận.
- Topic 9: 4 dự đoán tích cực; ví dụ đã che liên hệ: Mình mới mua con roborock kia dùng thấy oke. Đmx đag trợ giá rất tốt. Dùng chế độ nước nóng thì nhanh hết pin lắm còn dùng chế độ auto thì dọn được cả nhà ạ. | mua con lau xoay dùng ngon lành hơn nhiều, không lên ham hố lau con lăn. Đây là ví dụ mô hình gán tích cực, chưa phải đánh giá hài lòng được xác nhận.

## Chủ đề thảo luận
Tên chủ đề là nhãn gợi ý từ từ khóa và câu đại diện, cần người duyệt. Mẫu số gồm cả topic -1.
### Chủ đề 0: Hỏi giá và trao đổi ngắn
310 bình luận (33.26% toàn bộ mẫu giữ lại). Từ khóa: b; bác; xin; xin giá; ko; nó; ra; đây; giá; con.
Ví dụ: Xin giá bác ! | Xin giá nha b

### Chủ đề 1: Giá mua và nơi bán
141 bình luận (15.13% toàn bộ mẫu giữ lại). Từ khóa: mua; giá; bác; bán; hàng; k; con; hãng; năm; tr.
Ví dụ: Giá bnhiu bác | Chị cũng đang tính mua con này ,e mua con này giá nhiêu vậy e ?

### Chủ đề -1: Khác / Chưa phân nhóm
128 bình luận (13.73% toàn bộ mẫu giữ lại). Từ khóa: dùng; nó; saros; app; nhà; mới; ko; con; nước; giá.
Ví dụ: B nói đúng, cái bệ cũng ko quá quan trọng mấy đâu, cứ bảo bệ sạch thì giẻ mới sạch cũng ko hoàn toàn đúng, kể cả mấy con lau xoay, cái tấm chà giẻ nó cao hơn hẳn, bụi bẩn khi giặt giẻ sẽ rơi xuống dưới nên cũng ko ảnh hưởng j đến việc giặt giẻ. Nhưng khuyến cáo điều dùng robot là phải vệ sinh cho máy và dock thường xuyên, tuần 1 tuần hoặc tối đa là 1 tháng 1 lần chứ lười để vài tháng mới rờ đến máy là dễ hỏng lắm | t30c prime nhà mình dùng thích ạ, lực hút ổn 25k, có tự giặt giẻ, tự nâng giẻ, không có xoè giẻ vs giặt nước nóng thì phải. Mà nhà nhu cầu cơ bản thì vậy là ổn r

### Chủ đề 2: Nước lau và vệ sinh trạm
109 bình luận (11.70% toàn bộ mẫu giữ lại). Từ khóa: nước; lau; vệ_sinh; bị; sạch; không; nước lau; xem; đổ; nó.
Ví dụ: Hộp đựng nước lau sàn. B đổ nước lau sàn vào đó. Nó sẽ tự động pha nhé | vệ sinh phần hộc giặt sạch sẽ đi bác, vệ sinh cả bình nước bẩn, lau khô gioăng cao su ở nắp rồi đóng chặt lại thử xem Tình trạng của mình là máy k hút đc nước bẩn lên

### Chủ đề 3: Robot và máy lau hút cầm tay
62 bình luận (6.65% toàn bộ mẫu giữ lại). Từ khóa: robot; hút; lau; nhà; máy; sạch; sàn; bụi; hút bụi; mua.
Ví dụ: Giờ bê lên xuống các tầng thì phải bê cả trạm cả máy vừa nặng vừa cồng kềnh, đi tơi đi lui 2 lượt, còn phải rút điện trạm sạc nữa, bất tiện phết Thì giờ 1 là mình chấp nhận điều đó và chịu khó bê thôi 2 hợp lý hơn thì là cân đối tài chính làm mỗi tầng 1 máy 3 là mua máy lau hút sàn cầm tay, có trợ lực nên dùng cũng nhẹ tênh, k lo tốn sức nhiều, làm sạch thì chắc chắn hơn robot rồi, đặc biệt khả năng xử lý vết bẩn lỏng như đồ ăn thức uống đổ ra sàn, chủ động hơn trong việc sử dụng, làm sạch tại c | 20m2 thì mua máy hút bụi dc r b :)) máy hút bụi cầm tay còn tiện hút dc lông mèo ở ngõ ngách :) nhà rộng rộng mới mua robot thôi. Hoặc b dư dả thì mua con máy cây lau hút xong mua thêm 1 con hút cầm tay hút dc mấy khe nhỏ vs máy hút nệm là dc r :))

### Chủ đề 4: So sánh mẫu máy và tính năng
53 bình luận (5.69% toàn bộ mẫu giữ lại). Từ khóa: hơn; t90; t50; t80; t30c; về; omni; rồi; công_nghệ; hút.
Ví dụ: X50 thì khỏi so sánh cùng rồi, so sánh giứa T90 và Saros 20 thì về vận hành hay cách thức dọn dẹp thì tương tự nhau rồi, còn về tính năng, công nghệ thì T90 hơn ạ - Nâng được con lăn 15mm (saros 8mm) - Sạc nhanh gấp 5 lần, chạy thoải mái tới 1000m2 trong 1 lần (saros k có chạy được 250m2) - Công nghệ hút lốc xoáy Blast mới hút hiệu quả mà tiết kiệm điện năng - Lau con lăn sạch nhất hiện tại, không để lại vệt nước (saros lau rung ồn, dễ hỏng hơn do động cơ rung liên tục lâu dài và tốn giẻ lau, vẫ | Công năng thì gần tương tự nhau rồi, T90 ra sau nên nâng cấp, cải tiến hơn chút, thiết kế con lăn dài hơn 50% giúp bao phủ diện tích rộng hơn khi di chuyển nên là làm sạch nhanh hơn gấp 2 lần, lực hút mạnh hơn nữa lên tới 30000Pa, chổi chống rối đời mới tối ưu hơn nữa và công nghệ nhận diện né tránh vật cản thông minh hơn với bản 4.0. Còn X11 Pro thuộc dòng X là phân khúc cao cấp nhất với độ hoàn thiện về chất lượng và thiết kế tốt hơn, em thấy dùng ổn định, chạy mượt, chắc chắn, ít khi xảy ra v

### Chủ đề 5: Lựa chọn dòng Roborock Qrevo
50 bình luận (5.36% toàn bộ mẫu giữ lại). Từ khóa: v1; pro; roborock; qrevo; curv; flow; edge; hơn; b; s pro.
Ví dụ: S Pro Roborock b nhé, xuất sắc nhất | 10tr lấy Qrevo S Pro của Roborock dùng rất ổn định luôn ạ

### Chủ đề 6: Độ bền và sửa chữa
26 bình luận (2.79% toàn bộ mẫu giữ lại). Từ khóa: cảm_biến; lỗi; máy; main; gửi; rồi; hỏng; sửa; bảo_hành; quạt.
Ví dụ: Lỗi cảm biến rồi :v | Lỗi E7 là lỗi main bên trong máy mình gửi hãng bảo hành sửa máy chị nha

### Chủ đề 7: So sánh X11 và T90
20 bình luận (2.15% toàn bộ mẫu giữ lại). Từ khóa: x11; new; tầm tr; hơn; tr; tầm; giá; x11 pro; pro; steam.
Ví dụ: Chị thích thiết kế đẹp trải nghiệm tốt thì x11 còn T90 thì rẻ hơn nhưng đọ thiết kế và trải nghiệm sẽ thua x11 còn tính năng và công nghệ thì ngang nhau | X11 Pro thuộc phân khúc cao cấp hơn, chất liệu thân vỏ và độ hoàn thiện đều hơn bác nhé

### Chủ đề 8: Sử dụng tại nhà và khoảng trống gầm
18 bình luận (1.93% toàn bộ mẫu giữ lại). Từ khóa: nhà; tầng; hải_phòng; đc ko; ko; phòng; đc; khách; nhà cũng; con.
Ví dụ: Tắt công tắc song bật lại xem có đc ko. Mấy lần nhà mình cũng bị thế | Gầm ghế sofa có chui đc ko ạ, mà ghế sofa phòng khách mình đi dây điện dưới đó để cho đẹp nhà gầm tối v con này có nhận diện đc ko nhỉ

### Chủ đề 9: Pin và chế độ vận hành
15 bình luận (1.61% toàn bộ mẫu giữ lại). Từ khóa: pin; xanh; chạy; mới mua; chế_độ; mua; mua con; nhưng; kh; hàng.
Ví dụ: E nghe bảo giẻ bán nguyệt lau kh tốt như xoay hay con lăn nhưng nó lau bằng nước ấm nên e nghĩ sẽ sạch, mà giờ em thấy mã cao cấp thì nhiều có ecovas đồ các kiểu, nhưng em vẫn bị thích cách đi map của roborock nó kh bị ngoo như mấy hãng kia | Mình mới mua con roborock kia dùng thấy oke. Đmx đag trợ giá rất tốt. Dùng chế độ nước nóng thì nhanh hết pin lắm còn dùng chế độ auto thì dọn được cả nhà ạ.

## Vướng mắc cụ thể và cơ hội ưu tiên
Các số sau là bình luận ứng viên khớp quy tắc công khai trong pain_point_evidence.csv, có thể gồm câu hỏi, chẩn đoán hoặc lời khuyên; không phải số sự cố đã xác nhận, không phải tỷ lệ khách hàng bị lỗi. Các nhóm có thể chồng lấp. Ưu tiên thăm dò theo số đề cập, chưa đo mức nghiêm trọng hay hiệu quả kinh doanh.
### Ưu tiên 1: Lỗi cảm biến hoặc bo mạch
14 bình luận ứng viên (1.50% trên 932); topic 0, 6.
Ví dụ: Lỗi cảm biến trên khay rồi bác . Hà Nội mình nhận sửa nhé bạn. [ADDRESS] | Lỗi cảm biến rồi
Giả thuyết cơ hội: Dịch vụ: quy trình chẩn đoán, báo giá và xác nhận lỗi trước khi thay bo mạch.

### Ưu tiên 2: Mùi giẻ và nhu cầu giặt/vệ sinh bằng tay
14 bình luận ứng viên (1.50% trên 932); topic -1, 0, 2, 3.
Ví dụ: Mùi của miếng lọc hepa hay sao ấy. Nó bị ướt nên có mùi hôi á | Robot tự giặt giẻ chỉ tạm dc Khoản 2-3 tuần tháo giẻ ngâm và giặt tay nhé
Giả thuyết cơ hội: Nội dung: lịch vệ sinh và cách xử lý mùi theo hướng dẫn hãng; không khuyến nghị hóa chất theo bình luận.

### Ưu tiên 3: Gầm thấp, vật cản và dây điện
8 bình luận ứng viên (0.86% trên 932); topic -1, 2, 3, 4, 8.
Ví dụ: Để chọn được mẫu phù hợp với túi tiền và nhu cầu sử dụng thì em cần biết diện tích nhà mình, loại sàn, tình trạng độ bẩn của sàn, có nhiều gầm thấp không, có dùng thảm không và quan trọng ngân sách khoảng bao nhiêu ạ | Gầm ghế sofa có chui đc ko ạ, mà ghế sofa phòng khách mình đi dây điện dưới đó để cho đẹp nhà gầm tối v con này có nhận diện đc ko nhỉ
Giả thuyết cơ hội: Sản phẩm/nội dung: công bố chiều cao thực tế, khả năng vượt bậc và thử nghiệm vật cản.

### Ưu tiên 4: Pin, khởi động và sạc
7 bình luận ứng viên (0.75% trên 932); topic -1, 0, 9.
Ví dụ: Mình mới mua con roborock kia dùng thấy oke. Đmx đag trợ giá rất tốt. Dùng chế độ nước nóng thì nhanh hết pin lắm còn dùng chế độ auto thì dọn được cả nhà ạ. | Chai pin rùi b
Giả thuyết cơ hội: Sản phẩm/nội dung: công bố thời lượng theo chế độ, hướng dẫn sạc và kiểm tra tiếp điểm.

### Ưu tiên 5: Chi phí sửa và thời gian/kết quả bảo hành
7 bình luận ứng viên (0.75% trên 932); topic -1, 0, 1, 3, 6, 8.
Ví dụ: Con này mà sửa tầm 1tr mình khuyên khách ko nên sửa, tầm 500k đổ lại thì ok | Có Bác nào bị hỏng main như nhà e không! Họ báo sửa hết 3,5 tr! Trong khi lúc chưa mang đi ra hiệu sửa, máy chỉ báo hỏng cảm ứng chống rơi!
Giả thuyết cơ hội: Dịch vụ: báo giá minh bạch, thời hạn xử lý và cơ chế theo dõi bảo hành.

### Ưu tiên 6: Hút nước bẩn, độ kín bình và khay giặt
6 bình luận ứng viên (0.64% trên 932); topic 2.
Ví dụ: Cái bình nước sạch của bác có bị lỏng như này không ạ | Khi máy tự động giặc giẻ xong thì đổ nước bẩn thử đi bạn, xem hết mùi hôi không Bạn có dùng nước lau sàn nào không?
Giả thuyết cơ hội: Sản phẩm/dịch vụ: kiểm tra độ kín bình, đường hút nước và hướng dẫn vệ sinh khay.

### Ưu tiên 7: Bê máy và trạm giữa các tầng
5 bình luận ứng viên (0.54% trên 932); topic 0, 2, 3, 8.
Ví dụ: Làm ngay 1 cặp này đi chị. Khỏi phải bê đi bê lại | Giờ bê lên xuống các tầng thì phải bê cả trạm cả máy vừa nặng vừa cồng kềnh, đi tơi đi lui 2 lượt, còn phải rút điện trạm sạc nữa, bất tiện phết Thì giờ 1 là mình chấp nhận điều đó và chịu khó bê thôi 2 hợp lý hơn thì là cân đối tài chính làm mỗi tầng 1 máy 3 là mua máy lau hút sàn cầm tay, có trợ lực nên dùng cũng nhẹ tênh, k lo tốn sức nhiều, làm sạch thì chắc chắn hơn robot rồi, đặc biệt khả năng xử lý vết bẩn lỏng như đồ ăn thức uống đổ ra sàn, chủ động hơn trong việc sử dụng, làm sạch tại c
Giả thuyết cơ hội: Sản phẩm/nội dung: tư vấn cấu hình theo số tầng, cân nhắc máy cầm tay và tổng chi phí.

### Ưu tiên 8: Khóa app và khó khăn cài đặt
5 bình luận ứng viên (0.54% trên 932); topic -1, 3.
Ví dụ: Mua main nhỏ quốc tế zomo 900 gắn vô là xài vĩnh viễn kg sơ khóa app | Mấy con irobot này cài đặt vất vải luôn,vật vả mấy ngày nay tự vào được
Giả thuyết cơ hội: Dịch vụ/nội dung: làm rõ phiên bản, khả năng kết nối và hướng dẫn cài đặt tiếng Việt.

## Phụ lục dấu hiệu theo nhóm tính năng
Các nhóm dưới đây đếm bằng biểu thức từ khóa công khai; có thể chồng lấp. “Dấu hiệu vấn đề” không đồng nghĩa cảm xúc tiêu cực. Không suy diễn nguyên nhân mua hàng.
### Ưu tiên 1: Độ bền và sửa chữa
Đo lường: 24 bình luận có đồng thời từ khóa nhóm này và dấu hiệu vấn đề, trong 86 lượt đề cập nhóm. Đây là đồng xuất hiện trong bình luận, không khẳng định lỗi thuộc về tính năng đó. Chủ đề liên quan đến dấu hiệu vấn đề: -1, 0, 1, 2, 3, 4, 6, 9.
Ví dụ đã che liên hệ: Có Bác nào bị hỏng main như nhà e không! Họ báo sửa hết 3,5 tr! Trong khi lúc chưa mang đi ra hiệu sửa, máy chỉ báo hỏng cảm ứng chống rơi! | lỗi cảm biến mình cũng vừa bị . gửi bảo hành 10 ngày thì nhận lại dc máy
Giả thuyết cơ hội (ưu tiên theo số đề cập vấn đề, chưa kiểm chứng): Làm rõ bảo hành, chi phí sửa và khả năng mua linh kiện.

### Ưu tiên 2: Hiệu quả hút và lau
Đo lường: 15 bình luận có đồng thời từ khóa nhóm này và dấu hiệu vấn đề, trong 173 lượt đề cập nhóm. Đây là đồng xuất hiện trong bình luận, không khẳng định lỗi thuộc về tính năng đó. Chủ đề liên quan đến dấu hiệu vấn đề: -1, 0, 2, 3, 4, 9.
Ví dụ đã che liên hệ: lỗi chung rồi sống với lũ thôi e hỏi hãng mà hãng kêu vệ sinh sạch r gắn kkk | Trải nghiệm qua nhiều hãng, nhiều model robot thì e khá ngạc nhiên khi dùng thử con này. Hắn làm sạch, mà kĩ đến mức…tưởng hắn bị lỗi luôn á. Có những vị trí vỏn vẹn 1 2m2 mà hắn lau - giặt giẻ rồi quay lại lau tận 2 lần xong mới hút bụi
Giả thuyết cơ hội (ưu tiên theo số đề cập vấn đề, chưa kiểm chứng): Minh họa khả năng vệ sinh theo loại sàn và vết bẩn.

### Ưu tiên 3: Chi phí và lựa chọn sản phẩm
Đo lường: 14 bình luận có đồng thời từ khóa nhóm này và dấu hiệu vấn đề, trong 239 lượt đề cập nhóm. Đây là đồng xuất hiện trong bình luận, không khẳng định lỗi thuộc về tính năng đó. Chủ đề liên quan đến dấu hiệu vấn đề: -1, 1, 3, 4, 8, 9.
Ví dụ đã che liên hệ: Mình thì cứ báo lỗi 52, mua cái máy 20tr mà chán luôn | Tốt nhất mua loại ko tự tháo dẻ để tránh lỗi này. :d
Giả thuyết cơ hội (ưu tiên theo số đề cập vấn đề, chưa kiểm chứng): Công bố tổng chi phí và bảng so sánh theo nhu cầu.

### Ưu tiên 4: Tiếng ồn và mắc kẹt
Đo lường: 12 bình luận có đồng thời từ khóa nhóm này và dấu hiệu vấn đề, trong 13 lượt đề cập nhóm. Đây là đồng xuất hiện trong bình luận, không khẳng định lỗi thuộc về tính năng đó. Chủ đề liên quan đến dấu hiệu vấn đề: -1, 0, 2, 4, 5, 6.
Ví dụ đã che liên hệ: Xem kẹt ko đã b | Bác tháo ra vệ sinh xem có vướng hay kẹt tóc không. Nếu không thì khả năng lỗi trục Hà Nội mình nhận sửa nhé bạn. [ADDRESS]
Giả thuyết cơ hội (ưu tiên theo số đề cập vấn đề, chưa kiểm chứng): Nêu giới hạn vận hành và cách chuẩn bị không gian.

### Ưu tiên 5: Nước và vệ sinh trạm
Đo lường: 10 bình luận có đồng thời từ khóa nhóm này và dấu hiệu vấn đề, trong 110 lượt đề cập nhóm. Đây là đồng xuất hiện trong bình luận, không khẳng định lỗi thuộc về tính năng đó. Chủ đề liên quan đến dấu hiệu vấn đề: -1, 2, 3, 4.
Ví dụ đã che liên hệ: Trải nghiệm qua nhiều hãng, nhiều model robot thì e khá ngạc nhiên khi dùng thử con này. Hắn làm sạch, mà kĩ đến mức…tưởng hắn bị lỗi luôn á. Có những vị trí vỏn vẹn 1 2m2 mà hắn lau - giặt giẻ rồi quay lại lau tận 2 lần xong mới hút bụi | Viên xanh nhạt ion bạc ag+ khử mùi khử khuẩn nước, còn cái phao kia có nam châm để báo mức nước bạn lấy ra nó báo đỏ đèn đúng rùi. Mua cục khác bỏ vô thui. Mình bán cả 2 cho bình nước sạch+bẩn nhé
Giả thuyết cơ hội (ưu tiên theo số đề cập vấn đề, chưa kiểm chứng): Giải thích bảo trì trạm, bình nước và lịch vệ sinh.

### Ưu tiên 6: Cảm biến và điều hướng
Đo lường: 8 bình luận có đồng thời từ khóa nhóm này và dấu hiệu vấn đề, trong 19 lượt đề cập nhóm. Đây là đồng xuất hiện trong bình luận, không khẳng định lỗi thuộc về tính năng đó. Chủ đề liên quan đến dấu hiệu vấn đề: 6.
Ví dụ đã che liên hệ: Lỗi cảm biến trên khay rồi bác . Hà Nội mình nhận sửa nhé bạn. [ADDRESS] | Lỗi cảm biến rồi
Giả thuyết cơ hội (ưu tiên theo số đề cập vấn đề, chưa kiểm chứng): Cung cấp hướng dẫn xử lý cảm biến và khôi phục bản đồ.

### Ưu tiên 7: Pin và sạc
Đo lường: 6 bình luận có đồng thời từ khóa nhóm này và dấu hiệu vấn đề, trong 27 lượt đề cập nhóm. Đây là đồng xuất hiện trong bình luận, không khẳng định lỗi thuộc về tính năng đó. Chủ đề liên quan đến dấu hiệu vấn đề: 0, 4, 9.
Ví dụ đã che liên hệ: Bác đưa vào dock sạc nó phải khởi động được lên đèn. Nếu không lên thì lỗi bo mạch rồi nhé bác. Hà Nội mình nhận sửa nhé bạn. [ADDRESS] | Trước mình mới mua con saros 10r. Lần đầu chạy cũng lỗi. Nhưng sau đó để nó sạc pin no căng, tiện xem có update thì nâng lên luôn. Xong hết thì thấy chạy bình thường lại. Có khi mới mua về mà chạy luôn là lỗi đó bạn. Đợi pin đầy chạy xem sao.
Giả thuyết cơ hội (ưu tiên theo số đề cập vấn đề, chưa kiểm chứng): Thử nghiệm thời lượng pin và hướng dẫn chẩn đoán sạc.

### Ưu tiên 8: Kết nối và ứng dụng
Đo lường: 1 bình luận có đồng thời từ khóa nhóm này và dấu hiệu vấn đề, trong 20 lượt đề cập nhóm. Đây là đồng xuất hiện trong bình luận, không khẳng định lỗi thuộc về tính năng đó. Chủ đề liên quan đến dấu hiệu vấn đề: 2.
Ví dụ đã che liên hệ: Bình nước bị lỏng do trong quá trình sử dụng, tháo lắp bị lỏng, van ko khít ko hút được nước lên để làm nóng cài thêm app xem trên đó báo cụ thể lỗi gì
Giả thuyết cơ hội (ưu tiên theo số đề cập vấn đề, chưa kiểm chứng): Hướng dẫn ghép nối và xử lý lỗi ứng dụng bằng tiếng Việt.

## Yếu tố được nhắc tới khi lựa chọn
Tần suất đề cập không chứng minh động cơ hay yếu tố gây ra quyết định mua.
- Chi phí và lựa chọn sản phẩm: 239 bình luận; topic -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9. Ví dụ: Đây là bình thường nhé. Máy có bơm cảm biến tự pha. Nên dùng đỡ tốn hơn. K sao cả đâu | Máy pha ít lắm tỉ lệ 1:200 thôi nên k tốn đâu b.
- Hiệu quả hút và lau: 173 bình luận; topic -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9. Ví dụ: Tôi dùng con Roborock 5V1, mỗi lần lau nó dùng ít nhất 1/3 bình đựng nước sạch. | B để ở chế độ giặt giẻ kĩ vs chế độ dùng nhiều nc lau sàn xem sao
- Nước và vệ sinh trạm: 110 bình luận; topic -1, 0, 1, 2, 3, 4, 5, 6, 9. Ví dụ: Tôi dùng con Roborock 5V1, mỗi lần lau nó dùng ít nhất 1/3 bình đựng nước sạch. | B để ở chế độ giặt giẻ kĩ vs chế độ dùng nhiều nc lau sàn xem sao
- Độ bền và sửa chữa: 86 bình luận; topic -1, 0, 1, 2, 3, 4, 6, 7, 8, 9. Ví dụ: Bà mua dung dịch nước rửa kính oto về pha . Một chai pha sài cả năm ko hết ý là tui sài bộ cấp xả ngày lau 2 lần đó. Vừa sạch vừa bóng. Tui dùng cả năm nay bữa tháo ra thay cái quạt hút cái bình nước sáng bóng. | Roborocks s7 max unltra giá 16tr bao lắp đặt vận chuyên tận nơi bảo hành 24 tháng chính hãng ạ
- Pin và sạc: 27 bình luận; topic -1, 0, 2, 3, 4, 9. Ví dụ: Mình mới mua con roborock kia dùng thấy oke. Đmx đag trợ giá rất tốt. Dùng chế độ nước nóng thì nhanh hết pin lắm còn dùng chế độ auto thì dọn được cả nhà ạ. | Bác đưa vào dock sạc nó phải khởi động được lên đèn. Nếu không lên thì lỗi bo mạch rồi nhé bác. Hà Nội mình nhận sửa nhé bạn. [ADDRESS]
- Kết nối và ứng dụng: 20 bình luận; topic -1, 2, 3, 5. Ví dụ: Mua main nhỏ quốc tế zomo 900 gắn vô là xài vĩnh viễn kg sơ khóa app | App mở rồi, ko mất tiền bạn a
- Cảm biến và điều hướng: 19 bình luận; topic -1, 0, 2, 3, 6. Ví dụ: Lỗi cảm biến trên khay rồi bác . Hà Nội mình nhận sửa nhé bạn. [ADDRESS] | Lỗi cảm biến rồi
- Tiếng ồn và mắc kẹt: 13 bình luận; topic -1, 0, 2, 4, 5, 6, 9. Ví dụ: Xem kẹt ko đã b | Bác tháo ra vệ sinh xem có vướng hay kẹt tóc không. Nếu không thì khả năng lỗi trục Hà Nội mình nhận sửa nhé bạn. [ADDRESS]

## Phân tích độ nhạy: chỉ organic
Giữ cố định topic của mô hình chính; không tái huấn luyện cụm, nên không đo độ ổn định khi tái huấn luyện.
- positive: 363/918 (39.54%).
- neutral: 343/918 (37.36%).
- negative: 212/918 (23.09%).

## Kiểm tra hành vi dự đoán — chưa có nhãn người
Trong 23 bình luận chứa “xin giá / giá bao nhiêu / giá bnhieu”, có 7 bị mô hình gán negative. Đây là dấu hiệu cần duyệt, không phải đo độ chính xác bằng nhãn chuẩn.
- Dòng Excel 417, topic 0: “Xin giá” → negative, độ tin cậy 0.950.
- Dòng Excel 418, topic 0: “Xin giá bạn ơi” → negative, độ tin cậy 0.840.
Có 7 bình luận bắt đầu bằng chẩn đoán “lỗi cảm biến / main / E7”; không được mặc định coi chẩn đoán là bất mãn.
- Dòng Excel 2, topic 6: “Lỗi cảm biến trên khay rồi bác . Hà Nội mình nhận sửa nhé bạn. [ADDRESS]” → negative.
- Dòng Excel 4, topic 6: “Lỗi cảm biến rồi” → negative.
Cụm lớn chứa trao đổi ngắn có thể trộn hỏi giá, chẩn đoán và phản hồi xã giao; không đồng nhất toàn bộ cụm với nhu cầu mua. Nhãn organic theo quy tắc không chứng minh tác giả là khách hàng; quảng cáo vẫn có thể lọt bộ lọc.
Nên dùng chủ đề, câu trích và mẫu kiểm tra để thăm dò; không dùng tỷ lệ cảm xúc làm KPI hài lòng hay suy diễn quy mô thị trường.

## Giới hạn và yêu cầu kiểm tra
- Mẫu nhóm Facebook không ngẫu nhiên; có quảng cáo và nội dung hỗn hợp. Không đại diện thị trường hay khách hàng duy nhất.
- Mô hình tiền huấn luyện có lệch miền; mỉa mai, phủ định và chẩn đoán như “lỗi cảm biến” có thể bị hiểu sai. Không tuyên bố độ chính xác đã được xác nhận.
- BERTopic/UMAP/HDBSCAN phụ thuộc tham số, seed và phiên bản. Chưa kiểm tra ổn định đa seed.
- Tên chủ đề, nhãn thương mại và mẫu cảm xúc cần người kiểm tra. Các cột human_label để trống; chưa có xác nhận của người gán nhãn.
- Xem sentiment_review_sample.csv để kiểm tra phủ định, chẩn đoán, nghi ngờ mỉa mai, nội dung thương mại hỗn hợp và độ tin cậy thấp.
- Văn bản dài có thể bị cắt khi phân loại: 0 bình luận.
- Embedding cắt ở giới hạn mô hình: 6 bình luận. Từ ngữ phủ định lỗi phổ biến được loại khỏi quy tắc dấu hiệu vấn đề, nhưng quy tắc vẫn có thể sai.
- Chi tiết mô hình, commit mô hình, phiên bản thư viện, thời gian và tham số có trong run_metadata.json.
