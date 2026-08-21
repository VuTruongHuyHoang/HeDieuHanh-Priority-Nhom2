# Mô phỏng lập lịch CPU Priority

Đồ án môn Hệ điều hành của Nhóm 2, xây dựng bằng Python và Tkinter nhằm mô phỏng, trực quan hóa và so sánh các thuật toán lập lịch CPU.

Repository dự án: [VuTruongHuyHoang/HeDieuHanh-Priority-Nhom2](https://github.com/VuTruongHuyHoang/HeDieuHanh-Priority-Nhom2)

## Chức năng chính

- Nhập tiến trình thủ công, tạo dữ liệu mẫu hoặc đọc tệp CSV theo cấu trúc `PID, AT, BT, PR`.
- Mô phỏng Priority Non-Preemptive và Priority Preemptive.
- Hỗ trợ Aging để hạn chế tình trạng starvation.
- Mô phỏng FCFS làm thuật toán đối chứng.
- Hiển thị biểu đồ Gantt và bảng kết quả `CT`, `TAT`, `WT`, `RT`.
- Theo dõi mô phỏng theo từng bước bằng Previous, Next và Play/Pause.
- So sánh FCFS với Priority trên cùng một bộ dữ liệu.
- Phân tích hàng loạt nhiều tệp CSV và xuất thống kê, bảng so sánh cùng biểu đồ SVG.

## Yêu cầu

- Python 3.13 trở lên.
- Tkinter (được tích hợp sẵn trong bản cài Python tiêu chuẩn trên Windows).

Dự án hiện không yêu cầu thư viện runtime bên thứ ba.

## Chạy ứng dụng

```powershell
git clone https://github.com/VuTruongHuyHoang/HeDieuHanh-Priority-Nhom2.git
cd HeDieuHanh-Priority-Nhom2
python main.py
```

Nếu sử dụng môi trường ảo tại thư mục dự án:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe main.py
```

Giao diện gồm ba khu vực chính:

1. **Detail Simulation**: chạy FCFS hoặc Priority và theo dõi từng bước.
2. **Comparison: FCFS vs Priority**: đối chiếu kết quả hai thuật toán.
3. **Batch Analysis**: phân tích một tệp hoặc thư mục chứa nhiều tệp CSV.

## Định dạng dữ liệu CSV

```csv
PID,AT,BT,PR
P1,0,5,3
P2,1,3,4
P3,2,4,2
P4,4,2,1
```

Trong đó:

- `PID`: mã tiến trình.
- `AT`: thời điểm tiến trình đến (Arrival Time).
- `BT`: thời gian CPU cần xử lý (Burst Time).
- `PR`: mức ưu tiên; số nhỏ hơn biểu thị mức ưu tiên cao hơn.

## Phân tích CSV bằng dòng lệnh

```powershell
python analyze.py --input <tep-hoac-thu-muc-csv> --output <thu-muc-ket-qua> --priority-mode both
```

Có thể bật Aging bằng tham số `--aging`:

```powershell
python analyze.py --input data --output output --priority-mode both --aging 2
```

Kết quả gồm các tệp thống kê chi tiết, bảng so sánh, bảng tổng hợp và biểu đồ SVG.

## Cấu trúc module

| Module | Vai trò |
| --- | --- |
| `module1_nhaplieu.py` | Nhập, kiểm tra và chuẩn hóa dữ liệu tiến trình |
| `module2_nonpreemptive.py` | Priority Non-Preemptive |
| `module3_preemptive.py` | Priority Preemptive |
| `module4_aging.py` | Tính Priority hiệu dụng và hỗ trợ Aging |
| `module5_bangketqua.py` | Hiển thị bảng kết quả và các chỉ số trung bình |
| `module6_ganttchart.py` | Trực quan hóa biểu đồ Gantt |
| `module7_fcfs.py` | Thuật toán FCFS đối chứng |
| `module8_mainui.py` | Giao diện chính và điều phối các module |
| `analyze.py` | Phân tích hàng loạt dữ liệu CSV |

## Chạy nhanh

Điểm khởi động của chương trình là [`main.py`](main.py). Sau khi mở ứng dụng, có thể dùng dữ liệu mẫu có sẵn và chọn thuật toán để chạy mô phỏng ngay.
