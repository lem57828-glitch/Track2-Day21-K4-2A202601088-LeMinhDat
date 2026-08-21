# Báo cáo — Income Model CI/CD Lab

## 1. Bộ siêu tham số đã chọn và lý do

Đã chạy 3 thí nghiệm với MLflow trên `train_batch1.csv` (22.361 mẫu), đánh giá trên `holdout.csv` (500 mẫu):

| n_estimators | learning_rate | max_depth | f1_score | accuracy |
|---|---|---|---|---|
| 100 (mặc định) | 0.1 | 3 | 0.7109 | 0.8780 |
| 50 | 0.05 | 2 | 0.6051 | 0.8460 |
| **200** | **0.1** | **5** | **0.7149** | 0.8740 |

Chọn bộ **n_estimators=200, learning_rate=0.1, max_depth=5** vì đạt F1 cao nhất (0.7149), vượt ngưỡng quality gate (≥0.65) với biên an toàn hợp lý. Bộ tham số yếu (50, 0.05, 2) cho F1 chỉ 0.6051 — dùng chính bộ này để kiểm chứng quality gate chặn triển khai thành công (job Quality Gate fail, job Release không chạy).

## 2. Vì sao ngưỡng chất lượng đặt trên F1 chứ không phải accuracy

Dữ liệu Adult mất cân bằng lớp: chỉ 24.8% mẫu thuộc lớp thu nhập cao (>50K). Một mô hình "luôn đoán thu nhập thấp" đạt **accuracy = 0.752** nhưng **f1_score = 0.000** — không bắt được một trường hợp thu nhập cao nào, hoàn toàn vô dụng trong thực tế.

Số liệu thật từ 3 lần chạy trên cho thấy rõ điều này: accuracy gần như đứng yên quanh 0.87-0.88 giữa các lần chạy (chênh lệch tối đa 0.032), trong khi f1_score dao động mạnh hơn nhiều, từ 0.6051 đến 0.7149 (chênh lệch 0.11) — accuracy "khen" cả mô hình yếu, còn f1_score mới phản ánh đúng khả năng nhận diện lớp thiểu số. Vì vậy quality gate phải đặt trên f1_score để không cho một mô hình học kém trót lọt ra sản phẩm.

## 3. So sánh F1 giữa 22.361 mẫu và 44.722 mẫu

Dùng cùng bộ tham số tốt nhất (200, 0.1, 5):

| Kích thước train | f1_score | accuracy |
|---|---|---|
| 22.361 mẫu | 0.7149 | 0.8740 |
| 44.722 mẫu (sau `append_batch.py`) | 0.7289 | 0.8780 |

F1 tăng nhẹ (+0.014) chứ không tăng vọt. Đúng như dự đoán: `train_batch2.csv` được chia ngẫu nhiên từ cùng nguồn dữ liệu với `train_batch1.csv` nên cùng phân phối — mô hình đã học gần hết những gì có thể học được từ 22.361 mẫu đầu, gấp đôi dữ liệu chỉ giúp ổn định thêm chút ít chứ không tạo đột phá. Điều quan trọng được kiểm chứng ở bước này không phải là chỉ số cao hơn, mà là **quy trình tự động chạy đúng**: chỉ một commit dữ liệu (`data: bo sung 22361 mau du lieu moi`) đã kích hoạt lại toàn bộ pipeline (4 job) và triển khai model mới lên VM mà không cần thao tác tay nào khác.

## 4. Khó khăn gặp phải và cách giải quyết

- **Azure for Students chặn VM**: tài khoản dùng email trường bị đẩy vào luồng đăng ký "tổ chức" (đòi mã VAT). Sau khi kích hoạt Azure for Students (không cần thẻ), storage account tạo được nhưng **mọi loại VM, ở cả 5 vùng được phép, đều bị chặn** (`SkuNotAvailable`/`NotAvailableForSubscription`) — chính sách chống lạm dụng của Microsoft với tài khoản sinh viên mới. Giải pháp: chuyển sang GCP.
- **GCP từ chối thẻ prepaid** (`OR_CCR_104`): thẻ Visa prepaid không được Google Cloud chấp nhận cho xác minh billing dưới mọi hình thức. Giải pháp: chuyển hẳn sang AWS, dùng đúng thẻ đó — AWS chấp nhận.
- **SSH deploy key không hoạt động** (`unable to authenticate`): lệnh tạo systemd service/append authorized_keys dùng heredoc lồng trong dấu ngoặc kép của SSH bị lỗi cú pháp khi dán qua CloudShell, khiến file/key không được tạo dù không báo lỗi rõ ràng. Giải pháp: chuyển sang mẫu `ssh host bash -s <<'EOF' ... EOF` (gửi script qua stdin), tránh lồng ngoặc kép, đồng thời luôn thêm bước `ls`/`cat` để xác minh file thực sự tồn tại trên VM trước khi chạy lại pipeline.
- **EC2 instance type không thuộc Free Tier**: `t2.micro` mặc định không được miễn phí ở region `ap-southeast-1` cho tài khoản này; tra `describe-instance-types --filters free-tier-eligible=true` để tìm đúng loại (`t3.micro`) trước khi tạo lại.
