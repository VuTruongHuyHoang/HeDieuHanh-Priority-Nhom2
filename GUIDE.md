# Hướng dẫn cài đặt và chạy project

## 1. Yêu cầu

Trước khi bắt đầu, máy cần có:

- Git.
- Python 3.13 trở lên.
- Tkinter đi kèm bản cài Python.

Kiểm tra Git và Python trên Windows:

```powershell
git --version
py -3.13 --version
```

## 2. Clone repository

Mở PowerShell tại thư mục muốn lưu project rồi chạy:

```powershell
git clone -b dev https://github.com/VuTruongHuyHoang/HeDieuHanh-Priority-Nhom2.git
cd HeDieuHanh-Priority-Nhom2
```

Tham số `-b dev` giúp clone và checkout trực tiếp branch `dev`.

Nếu đã clone repository trước đó:

```powershell
git switch dev
git pull origin dev
```

## 3. Tạo virtual environment

Tại thư mục gốc của project, chạy:

```powershell
py -3.13 -m venv .venv
```

Sau khi tạo, Python riêng của project nằm tại:

```text
.venv\Scripts\python.exe
```

Không commit folder `.venv` lên GitHub.

## 4. Cài requirements

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Project hiện không có package bên thứ ba bắt buộc. Lệnh này vẫn cần được giữ
trong quy trình để tự động cài dependency nếu `requirements.txt` thay đổi sau
này.

## 5. Chạy ứng dụng

```powershell
.\.venv\Scripts\python.exe main.py
```

Cửa sổ `CPU Scheduling Simulator - Detail & Comparison` sẽ được mở.

## 6. Nhập dữ liệu tiến trình

Khu vực `Process Input` là dữ liệu dùng chung cho cả Detail Simulation và
Detail Comparison.

| Trường | Ý nghĩa | Giá trị hợp lệ |
|---|---|---|
| `PID` | Tên tiến trình | Chuỗi không rỗng và không trùng |
| `AT` | Arrival Time | Số nguyên `>= 0` |
| `BT` | Burst Time | Số nguyên `> 0` |
| `Priority` | Độ ưu tiên | Số nguyên `> 0` |

Priority có giá trị số nhỏ hơn thì mức ưu tiên cao hơn. Ví dụ, Priority `1`
được ưu tiên hơn Priority `3`.

### Thêm tiến trình

1. Nhập đủ PID, AT, BT và Priority.
2. Nhấn `Add`.
3. Kiểm tra dòng mới trong bảng Process Input.

Nếu dữ liệu sai hoặc PID đã tồn tại, ứng dụng sẽ hiển thị thông báo lỗi.

### Các nút quản lý dữ liệu

| Nút | Chức năng |
|---|---|
| `Add` | Thêm tiến trình mới |
| `Delete` | Xóa các dòng đang chọn |
| `Example` | Thay dữ liệu hiện tại bằng bộ dữ liệu mẫu |
| `Clear` | Xóa toàn bộ tiến trình |

Mỗi lần thay đổi Process Input, simulation và comparison cũ sẽ được reset. Cần
nhấn Prepare lại để kết quả sử dụng dữ liệu mới.

## 7. Sử dụng Detail Simulation

Mở tab `1. Detail Simulation` để quan sát một thuật toán theo từng bước.

### Chọn thuật toán

Ô `Algorithm` có hai lựa chọn:

- `Priority`
- `FCFS`

Nếu chọn Priority, chọn thêm `Priority Mode`:

- `Preemptive`: tiến trình đang chạy có thể bị tạm dừng khi có tiến trình ưu
  tiên cao hơn.
- `Non-Preemptive`: tiến trình đã nhận CPU chạy đến khi hoàn thành.

Khi chọn FCFS, Priority Mode và Aging không ảnh hưởng kết quả.

### Bật Aging cho Priority

1. Chọn `Priority`.
2. Đánh dấu `Aging`.
3. Nhập Aging Interval là số nguyên lớn hơn 0, ví dụ `5`.

Aging giúp tiến trình chờ lâu tăng dần mức ưu tiên và giảm nguy cơ starvation.

### Chuẩn bị và chạy simulation

1. Nhấn `Prepare` để tạo simulation từ Process Input hiện tại.
2. Dùng các nút điều khiển:

| Nút | Chức năng |
|---|---|
| `Previous` | Lùi một bước |
| `Play` | Tự động phát simulation |
| `Pause` | Tạm dừng playback |
| `Next` | Tiến một bước |

Ô `Speed` hỗ trợ `0.5x`, `1x`, `2x` và `5x`. Nếu simulation đã kết thúc, nhấn
Play sẽ chạy lại từ đầu.

### Đọc trạng thái scheduler

| Thành phần | Ý nghĩa |
|---|---|
| `TIME` | Khoảng thời gian của bước hiện tại |
| `EVENT` | Sự kiện scheduler |
| `CPU` | PID đang dùng CPU |
| `Step x/y` | Bước hiện tại trên tổng số bước |

Các event thường gặp gồm `START`, `EXEC`, `NEW ARRIVAL / EXEC`, `PREEMPTED`,
`FINISHED` và `CPU IDLE`.

### Đọc Ready Queue

| Cột | Ý nghĩa |
|---|---|
| `PID` | Tiến trình đang chờ CPU |
| `Remaining` | Burst Time còn lại |
| `PR` | Priority gốc |
| `Effective PR` | Priority sau khi áp dụng Aging |

Tiến trình đang chạy không nằm trong Ready Queue của bước đó.

### Đọc Gantt Chart

- Mỗi khối biểu thị PID chạy trong một khoảng thời gian.
- `Idle` nghĩa là CPU chưa có tiến trình sẵn sàng.
- Các số dưới biểu đồ là mốc thời gian.
- `Explanation` giải thích lý do scheduler chọn tiến trình hiện tại.

### Đọc Final Metrics

Final Metrics chỉ hiển thị đầy đủ khi simulation đến bước cuối.

| Cột | Ý nghĩa | Công thức |
|---|---|---|
| `PID` | Tên tiến trình | — |
| `AT` | Arrival Time | Dữ liệu nhập |
| `BT` | Burst Time | Dữ liệu nhập |
| `PR` | Priority | Dữ liệu nhập |
| `CT` | Completion Time | Thời điểm hoàn thành |
| `TAT` | Turnaround Time | `CT - AT` |
| `WT` | Waiting Time | `TAT - BT` |
| `RT` | Response Time | Thời điểm chạy lần đầu `- AT` |

Dòng tổng kết hiển thị Average WT, Average TAT, Average RT và số Context
Switch.

## 8. Sử dụng Detail Comparison

Mở tab `2. Detail Comparison` để chạy năm thuật toán trên cùng Process Input:

1. FCFS
2. SJF Non-Preemptive
3. SRTF Preemptive
4. Priority
5. Round Robin

### Cấu hình

| Tùy chọn | Cách dùng |
|---|---|
| `Priority mode` | Chọn Preemptive hoặc Non-Preemptive |
| `Priority Aging` | Bật Aging cho thuật toán Priority |
| Aging Interval | Nhập số nguyên lớn hơn 0 khi bật Aging |
| `RR Quantum` | Nhập Time Quantum lớn hơn 0 cho Round Robin |
| `Speed` | Chọn tốc độ playback |

### Chạy comparison

1. Kiểm tra Process Input.
2. Chọn Priority Mode, Aging và RR Quantum.
3. Nhấn `Prepare 5 Algorithms`.
4. Dùng Previous, Play/Pause hoặc Next để điều khiển timeline.

Mỗi hàng Gantt Chart tương ứng một thuật toán và dùng chung thang thời gian.
Khi timeline chưa kết thúc, cột `Running` cho biết tiến trình hiện tại.

Khi timeline hoàn tất, Comparison Metrics hiển thị Average WT, Average TAT,
Average RT và Context Switch. Phần `Evaluation` cho biết thuật toán tốt nhất theo
từng chỉ số và so sánh Priority với FCFS trên workload hiện tại.

## 9. Ví dụ sử dụng nhanh

Nhấn `Example`, sau đó thử:

1. Detail Simulation với `Priority` + `Preemptive`.
2. Dùng Next để quan sát từng quyết định và đọc Final Metrics ở bước cuối.
3. Chạy lại Detail Simulation với `FCFS`.
4. Mở Detail Comparison và nhấn `Prepare 5 Algorithms`.
5. Nhấn Play, sau đó đọc bảng Comparison Metrics và Evaluation.

## 10. Chạy kiểm thử

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Kết quả thành công sẽ kết thúc bằng:

```text
OK
```

## 11. Cập nhật source mới nhất

Trước khi bắt đầu làm việc:

```powershell
git switch dev
git pull origin dev
```

Sau khi pull, nếu `requirements.txt` có thay đổi, chạy lại:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 12. Kích hoạt môi trường tùy chọn

Không bắt buộc kích hoạt venv vì các lệnh trên gọi trực tiếp Python của project.
Nếu muốn kích hoạt trong PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Sau khi kích hoạt, có thể chạy:

```powershell
python main.py
python -m unittest discover -s tests -v
```

Thoát khỏi môi trường:

```powershell
deactivate
```

Nếu PowerShell chặn `Activate.ps1`, không cần thay đổi Execution Policy. Hãy
tiếp tục dùng lệnh đầy đủ:

```powershell
.\.venv\Scripts\python.exe main.py
```

## 13. Xử lý lỗi thường gặp

### Không tìm thấy Python 3.13

Cài Python 3.13, sau đó đóng và mở lại terminal. Kiểm tra lại:

```powershell
py -3.13 --version
```

### Không mở được giao diện Tkinter

Kiểm tra Tkinter:

```powershell
.\.venv\Scripts\python.exe -m tkinter
```

Nếu không xuất hiện cửa sổ kiểm tra, cài lại Python và bảo đảm thành phần Tcl/Tk
được chọn trong trình cài đặt.

### Môi trường `.venv` bị lỗi

Xóa `.venv`, tạo lại môi trường rồi cài requirements lại. Không sao chép venv
từ máy khác vì đường dẫn và Python có thể không tương thích.

### Source local bị cũ

```powershell
git switch dev
git pull origin dev
```

Nếu đang có thay đổi chưa commit, kiểm tra bằng `git status` trước khi pull để
tránh xung đột.

### PID mới chưa xuất hiện trong Final Metrics

Sau khi thêm PID, nhấn Prepare lại rồi dùng Play hoặc Next đến bước cuối.

### Metrics trong Comparison vẫn là dấu gạch

Metrics cuối chỉ xuất hiện khi timeline hoàn tất. Tiếp tục Play hoặc Next đến
thời điểm cuối.

### Input không hợp lệ

- PID phải khác rỗng và không trùng.
- AT phải là số nguyên không âm.
- BT và Priority phải là số nguyên dương.
- Aging Interval và RR Quantum phải là số nguyên lớn hơn 0 khi được sử dụng.

## 14. Quy trình đầy đủ trên máy mới

Với máy mới, có thể thực hiện lần lượt:

```powershell
git clone -b dev https://github.com/VuTruongHuyHoang/HeDieuHanh-Priority-Nhom2.git
cd HeDieuHanh-Priority-Nhom2
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe main.py
```
