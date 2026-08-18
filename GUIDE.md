# Hướng dẫn sử dụng Priority Scheduling Demo V2

## 1. Giới thiệu

Priority Scheduling Demo V2 là ứng dụng Python/Tkinter dùng để:

- Mô phỏng chi tiết Priority Scheduling và FCFS theo từng bước.
- Quan sát CPU, Ready Queue, sự kiện và Gantt Chart.
- Xem các chỉ số CT, TAT, WT và RT của từng tiến trình.
- So sánh FCFS, SJF, SRTF, Priority và Round Robin trên cùng dữ liệu.

## 2. Yêu cầu hệ thống

- Windows.
- Python 3.13 trở lên, có Tkinter.
- Không cần cài thư viện Python bên thứ ba.

Kiểm tra Python:

```powershell
py -3.13 --version
```

## 3. Chuẩn bị môi trường

Mở PowerShell tại thư mục project:

```powershell
cd D:\HDH\Priority
```

Tạo virtual environment nếu chưa có:

```powershell
py -3.13 -m venv .venv
```

Cài requirements:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Project hiện không có dependency pip bắt buộc. Lệnh trên vẫn nên được chạy để
giữ đúng quy trình khi `requirements.txt` được bổ sung sau này.

## 4. Khởi chạy ứng dụng

```powershell
.\.venv\Scripts\python.exe main.py
```

Cửa sổ `CPU Scheduling Simulator - Detail & Comparison` sẽ xuất hiện. Ứng dụng
tự nạp bốn tiến trình mẫu khi khởi động.

## 5. Process Input

Process Input là dữ liệu dùng chung cho cả Detail Simulation và Detail
Comparison.

### 5.1. Ý nghĩa các trường

| Trường | Ý nghĩa | Giá trị hợp lệ |
|---|---|---|
| `PID` | Tên tiến trình | Chuỗi không rỗng và không trùng |
| `AT` | Arrival Time | Số nguyên `>= 0` |
| `BT` | Burst Time | Số nguyên `> 0` |
| `Priority` | Độ ưu tiên | Số nguyên `> 0` |

Trong Priority Scheduling, số Priority nhỏ hơn biểu thị mức ưu tiên cao hơn.
Ví dụ, Priority `1` được ưu tiên hơn Priority `3`.

### 5.2. Thêm tiến trình

1. Nhập PID, AT, BT và Priority.
2. Nhấn `Add`.
3. Kiểm tra tiến trình mới trong bảng Process Input.

Ví dụ:

```text
PID      P5
AT       5
BT       4
Priority 2
```

Nếu dữ liệu sai hoặc PID đã tồn tại, ứng dụng sẽ hiển thị thông báo lỗi và
không thêm tiến trình.

### 5.3. Xóa tiến trình

1. Chọn một hoặc nhiều dòng trong bảng.
2. Nhấn `Delete`.

### 5.4. Nạp dữ liệu mẫu

Nhấn `Example` để thay toàn bộ dữ liệu hiện tại bằng bộ mẫu:

| PID | AT | BT | Priority |
|---|---:|---:|---:|
| P1 | 0 | 5 | 3 |
| P2 | 1 | 2 | 1 |
| P3 | 2 | 1 | 2 |
| P4 | 4 | 3 | 2 |

### 5.5. Xóa toàn bộ

Nhấn `Clear` để xóa mọi tiến trình.

> Khi Add, Delete, Example hoặc Clear được thực hiện, simulation và comparison
> trước đó sẽ được reset. Hãy nhấn Prepare lại để kết quả khớp Process Input mới.

## 6. Detail Simulation

Mở tab `1. Detail Simulation` để quan sát một thuật toán theo từng bước.

### 6.1. Chọn thuật toán

Ô `Algorithm` chỉ có hai lựa chọn:

- `Priority`
- `FCFS`

Nếu chọn Priority, chọn thêm `Priority Mode`:

- `Preemptive`: tiến trình đang chạy có thể bị tạm dừng khi xuất hiện tiến
  trình có độ ưu tiên cao hơn.
- `Non-Preemptive`: tiến trình đã được cấp CPU sẽ chạy đến khi hoàn thành.

Khi chọn FCFS, Priority Mode và Aging không ảnh hưởng kết quả.

### 6.2. Sử dụng Aging

Aging giúp tiến trình chờ lâu tăng dần mức ưu tiên, giảm nguy cơ starvation.

1. Chọn thuật toán `Priority`.
2. Đánh dấu `Aging`.
3. Nhập Aging Interval lớn hơn 0, ví dụ `5`.

Sau mỗi Aging Interval thời gian chờ, Effective Priority được giảm một đơn vị,
nhưng không nhỏ hơn 1.

### 6.3. Chuẩn bị simulation

Nhấn `Prepare`. Ứng dụng lấy toàn bộ tiến trình đang có trong Process Input và
tạo simulation mới.

Sau Prepare, giao diện hiển thị bước đầu tiên. Final Metrics chưa hiển thị đầy
đủ cho đến khi simulation đến bước cuối.

### 6.4. Điều khiển playback

| Nút | Chức năng |
|---|---|
| `Previous` | Lùi một bước |
| `Play` | Tự động phát simulation |
| `Pause` | Tạm dừng playback |
| `Next` | Tiến một bước |

Ô `Speed` hỗ trợ:

- `0.5x`: chậm.
- `1x`: tốc độ mặc định.
- `2x`: nhanh gấp đôi.
- `5x`: tốc độ nhanh nhất.

Nếu simulation đã kết thúc và nhấn Play, timeline sẽ chạy lại từ đầu.

### 6.5. Đọc Current Scheduler State

| Thành phần | Ý nghĩa |
|---|---|
| `TIME` | Khoảng thời gian của bước hiện tại |
| `EVENT` | Sự kiện scheduler tại bước hiện tại |
| `CPU` | PID đang sử dụng CPU |
| `Step x/y` | Bước hiện tại trên tổng số bước |

Các event thường gặp:

- `START`: tiến trình bắt đầu chạy.
- `EXEC`: tiến trình tiếp tục chạy.
- `NEW ARRIVAL / EXEC`: có tiến trình mới đến nhưng CPU tiếp tục tiến trình
  hiện tại.
- `PREEMPTED`: tiến trình cũ bị tạm dừng.
- `FINISHED`: tiến trình hoàn thành.
- `CPU IDLE`: chưa có tiến trình sẵn sàng.

### 6.6. Đọc Ready Queue

| Cột | Ý nghĩa |
|---|---|
| `PID` | Tiến trình đang chờ CPU |
| `Remaining` | Burst Time còn lại |
| `PR` | Priority gốc |
| `Effective PR` | Priority sau khi áp dụng Aging |

Tiến trình đang chạy không nằm trong Ready Queue của bước đó.

### 6.7. Đọc Gantt Chart và Explanation

- Mỗi khối trên Gantt Chart thể hiện PID chạy trong một khoảng thời gian.
- `Idle` nghĩa là CPU đang chờ tiến trình đến.
- Các mốc số dưới Gantt Chart là thời gian bắt đầu/kết thúc segment.
- `Explanation` giải thích lý do scheduler chọn tiến trình hiện tại.

### 6.8. Đọc Final Metrics

Final Metrics chỉ xuất hiện đầy đủ ở bước cuối.

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

Dòng summary hiển thị:

- Average Waiting Time.
- Average Turnaround Time.
- Average Response Time.
- Context Switch Count.

Nếu vừa thêm hoặc xóa PID, phải nhấn `Prepare` và chạy simulation đến bước cuối
để Final Metrics phản ánh dữ liệu mới.

## 7. Detail Comparison

Mở tab `2. Detail Comparison` để so sánh năm thuật toán trên cùng Process Input:

1. FCFS
2. SJF Non-Preemptive
3. SRTF Preemptive
4. Priority
5. Round Robin

### 7.1. Cấu hình comparison

| Tùy chọn | Hướng dẫn |
|---|---|
| `Priority mode` | Chọn Preemptive hoặc Non-Preemptive cho dòng Priority |
| `Priority Aging` | Bật nếu muốn áp dụng Aging cho Priority |
| Aging Interval | Nhập số nguyên lớn hơn 0 |
| `RR Quantum` | Nhập Time Quantum lớn hơn 0 cho Round Robin |
| `Speed` | Chọn tốc độ playback |

### 7.2. Chạy comparison

1. Kiểm tra Process Input.
2. Cấu hình Priority và Round Robin.
3. Nhấn `Prepare 5 Algorithms`.
4. Dùng các nút Previous, Play/Pause và Next để điều khiển timeline.

Tất cả thuật toán dùng cùng input và cùng một trục thời gian để kết quả có thể
được đối chiếu trực tiếp.

### 7.3. Đọc Comparison Gantt

- Mỗi hàng tương ứng một thuật toán.
- Đường dọc biểu thị thời điểm timeline hiện tại.
- Các khối cho biết PID đang chạy ở từng thuật toán.
- Khi timeline chưa kết thúc, cột `Running` cho biết tiến trình hiện tại.

### 7.4. Đọc Comparison Metrics

Khi timeline hoàn tất, bảng hiển thị:

- Average Waiting Time.
- Average Turnaround Time.
- Average Response Time.
- Context Switch Count.

Phần `Evaluation` cho biết:

- Thuật toán có Average WT tốt nhất.
- Thuật toán có Average TAT tốt nhất.
- Thuật toán có Average RT tốt nhất.
- So sánh Average WT giữa Priority và FCFS.

Kết luận chỉ áp dụng cho bộ Process Input hiện tại. Không có thuật toán nào luôn
tối ưu cho mọi workload.

## 8. Quy trình sử dụng đề xuất

### Kiểm tra một thuật toán

1. Nhập hoặc nạp dữ liệu mẫu.
2. Mở Detail Simulation.
3. Chọn Priority hoặc FCFS.
4. Cấu hình Priority Mode/Aging nếu cần.
5. Nhấn Prepare.
6. Dùng Next để theo dõi từng quyết định.
7. Đi đến bước cuối và ghi nhận Final Metrics.

### So sánh nhiều thuật toán

1. Giữ nguyên Process Input đã dùng ở Detail Simulation.
2. Mở Detail Comparison.
3. Cấu hình Priority Mode, Aging và RR Quantum.
4. Nhấn Prepare 5 Algorithms.
5. Nhấn Play.
6. Đọc Comparison Metrics và Evaluation khi timeline hoàn tất.

## 9. Ví dụ nhanh

Với dữ liệu:

| PID | AT | BT | Priority |
|---|---:|---:|---:|
| P1 | 0 | 5 | 3 |
| P2 | 1 | 2 | 1 |
| P3 | 2 | 1 | 2 |

Thử hai lần Detail Simulation:

1. `Priority` + `Preemptive`.
2. `FCFS`.

Ở Priority Preemptive, P1 có thể bị P2 tạm dừng khi P2 đến vì `1` có ưu tiên
cao hơn `3`. Ở FCFS, P1 tiếp tục chạy đến khi hoàn thành vì đã đến trước.

Sau đó mở Comparison để đối chiếu Average WT, TAT, RT và số context switch.

## 10. Xử lý lỗi thường gặp

### Không mở được ứng dụng

Kiểm tra đúng Python trong virtual environment:

```powershell
.\.venv\Scripts\python.exe --version
```

Sau đó chạy lại:

```powershell
.\.venv\Scripts\python.exe main.py
```

### Báo PID bị trùng

PID không phân biệt chữ hoa/thường. `P1` và `p1` được xem là cùng một PID. Hãy
đổi sang tên khác.

### Báo AT, BT hoặc Priority không hợp lệ

- AT phải là số nguyên không âm.
- BT phải là số nguyên dương.
- Priority phải là số nguyên dương.

### Báo Aging Interval không hợp lệ

Nhập số nguyên lớn hơn 0, ví dụ `5`.

### Báo RR Quantum không hợp lệ

Nhập số nguyên lớn hơn 0, ví dụ `2`.

### PID mới chưa xuất hiện trong Final Metrics

Việc thay đổi Process Input sẽ reset kết quả cũ. Sau khi thêm PID:

1. Nhấn `Prepare` lại.
2. Nhấn Play hoặc Next đến bước cuối.
3. Kiểm tra lại Final Metrics.

### Metrics trong Comparison vẫn là dấu gạch

Đây là trạng thái bình thường khi timeline chưa hoàn tất. Tiếp tục Play hoặc
Next đến thời điểm cuối.

## 11. Chạy kiểm thử

Để kiểm tra project sau khi thay đổi code:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Kết quả hợp lệ phải kết thúc bằng `OK`.
