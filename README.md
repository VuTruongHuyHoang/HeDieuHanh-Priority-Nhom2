# Priority Scheduling Demo V2

Ứng dụng Python/Tkinter mô phỏng FCFS, SJF, SRTF, Priority Scheduling và
Round Robin. Main UI hỗ trợ xem từng bước, Ready Queue, Gantt Chart, bảng chỉ
số và so sánh năm thuật toán trên cùng một bộ dữ liệu.

## Chạy ứng dụng

Yêu cầu Python 3.13. Trên Windows:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe main.py
```

Chạy test không cần cài dependency ngoài:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Cấu trúc

- `model/`: model dữ liệu dùng chung.
- `service/module/`: tám module bắt buộc của đề tài.
- `service/misc/`: các engine/thuật toán bổ sung như SJF, SRTF và Round Robin.
- `module5_bangketqua.py`: vừa cung cấp dữ liệu trung lập để Main UI render,
  vừa có `ResultPanel` tự render để tái sử dụng độc lập.
- `module8_mainui.py`: giao diện Demo V2.
