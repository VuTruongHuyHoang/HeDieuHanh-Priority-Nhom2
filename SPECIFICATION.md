# Đặc tả hệ thống Priority Scheduling Demo V2

## 1. Thông tin tài liệu

| Thuộc tính | Giá trị |
|---|---|
| Tên hệ thống | Priority Scheduling Demo V2 |
| Phiên bản đặc tả | 1.0 |
| Nền tảng | Python 3.13, Tkinter |
| Entry point | `main.py` |
| Phạm vi | Mô phỏng, trực quan hóa và so sánh các thuật toán lập lịch CPU |

Tài liệu này mô tả hành vi đang được triển khai trong source code. Khi tài liệu
và chương trình khác nhau, source code và test hiện hành là bằng chứng xác nhận
hành vi thực tế.

## 2. Mục tiêu

Hệ thống cho phép người dùng:

1. Nhập danh sách tiến trình gồm PID, Arrival Time, Burst Time và Priority.
2. Mô phỏng chi tiết Priority Scheduling hoặc FCFS theo từng bước thời gian.
3. Quan sát CPU, Ready Queue, sự kiện lập lịch và Gantt Chart.
4. Xem chỉ số hoàn thành của từng tiến trình.
5. So sánh năm thuật toán trên cùng dữ liệu và cùng mốc thời gian.

## 3. Phạm vi chức năng

### 3.1. Detail Simulation

Danh sách thuật toán người dùng được phép chọn trong tab Detail Simulation chỉ
gồm:

- `Priority`
- `FCFS`

Khi chọn Priority, người dùng được chọn thêm một trong hai chế độ:

- `Preemptive`
- `Non-Preemptive`

Aging chỉ tác động đến Priority. Giá trị Aging Interval phải là số nguyên lớn
hơn 0. Nếu chọn FCFS, thiết lập Aging không làm thay đổi kết quả.

Detail Simulation phải hỗ trợ:

- `Prepare`: tạo một simulation mới từ toàn bộ dữ liệu Process Input hiện tại.
- `Previous`: lùi một bước.
- `Next`: tiến một bước.
- `Play/Pause`: phát hoặc tạm dừng simulation tự động.
- Tốc độ phát: `0.5x`, `1x`, `2x`, `5x`.
- Hiển thị thời gian, sự kiện, PID đang dùng CPU và số thứ tự bước.
- Hiển thị Ready Queue tại bước hiện tại.
- Hiển thị Gantt Chart đến thời điểm của bước hiện tại.
- Chỉ công bố Final Metrics khi simulation đến bước cuối.

### 3.2. Detail Comparison

Comparison phải chạy đúng năm thuật toán trên cùng danh sách tiến trình:

1. FCFS
2. SJF Non-Preemptive
3. SRTF Preemptive
4. Priority Preemptive hoặc Priority Non-Preemptive
5. Round Robin

Người dùng được cấu hình:

- Priority Mode: Preemptive hoặc Non-Preemptive.
- Aging và Aging Interval cho Priority.
- Time Quantum cho Round Robin; giá trị phải lớn hơn 0.
- Tốc độ phát timeline.

Comparison phải hiển thị Gantt Chart, tiến trình đang chạy và các chỉ số trung
bình của năm thuật toán. Các chỉ số cuối chỉ hiển thị đầy đủ khi timeline hoàn
tất.

## 4. Dữ liệu đầu vào

Mỗi tiến trình sử dụng model `Process` với bốn trường:

| Trường | Kiểu | Ràng buộc |
|---|---:|---|
| `pid` | `str` | Không rỗng; không trùng, không phân biệt hoa thường |
| `arrival` | `int` | `>= 0` |
| `burst` | `int` | `> 0` |
| `priority` | `int` | `> 0`; số nhỏ hơn có độ ưu tiên cao hơn |

Module nhập liệu phải chấp nhận:

- Một đối tượng `Process` đã hợp lệ.
- Mapping dạng cũ: `PID`, `AT`, `BT`, `PR`.
- Mapping trung lập: `pid`, `arrival`, `burst`, `priority`.

Các thao tác Process Input gồm Add, Delete, Example và Clear. Mỗi thay đổi danh
sách tiến trình phải vô hiệu hóa simulation và comparison đã chuẩn bị trước đó.

## 5. Quy tắc thuật toán

### 5.1. FCFS

- Chọn tiến trình có Arrival Time nhỏ nhất trong Ready Queue.
- Không preempt.
- Nếu cùng Arrival Time, dùng PID theo thứ tự tự nhiên để phá hòa, ví dụ `P2`
  đứng trước `P10`.

### 5.2. SJF Non-Preemptive

- Chọn tiến trình sẵn sàng có Burst Time nhỏ nhất.
- Tiến trình đã được chọn phải chạy đến khi hoàn thành.
- Phá hòa theo Arrival Time, sau đó theo PID tự nhiên.

### 5.3. SRTF Preemptive

- Chọn tiến trình sẵn sàng có Remaining Time nhỏ nhất tại mỗi tick.
- Cho phép preempt khi xuất hiện lựa chọn tốt hơn.
- Phá hòa theo Arrival Time, sau đó theo PID tự nhiên.

### 5.4. Priority Non-Preemptive

- Chọn tiến trình có Effective Priority nhỏ nhất.
- Tiến trình đã được chọn chạy đến khi hoàn thành.
- Phá hòa theo Arrival Time, sau đó theo PID tự nhiên.

### 5.5. Priority Preemptive

- Đánh giá lại Effective Priority tại mỗi tick.
- Cho phép preempt nếu tiến trình khác có khóa lựa chọn tốt hơn.
- Phá hòa theo Arrival Time, sau đó theo PID tự nhiên.

### 5.6. Aging

Aging dùng công thức:

```text
waiting = max(0, current_time - arrival - executed)
effective_priority = max(1, priority - floor(waiting / aging_interval))
```

Trong đó:

- `executed` là tổng thời gian CPU tiến trình đã thực thi.
- `aging_interval` phải lớn hơn 0.
- Effective Priority không được nhỏ hơn 1.
- Aging không sửa Priority gốc của tiến trình.

### 5.7. Round Robin

- Ready Queue hoạt động theo FIFO.
- Mỗi tiến trình chạy tối đa `quantum` đơn vị thời gian trong một lượt.
- Tiến trình chưa hoàn thành sau khi hết quantum được đưa về cuối hàng đợi.
- Tiến trình mới đến được thêm vào Ready Queue theo Arrival Time và PID tự nhiên.

### 5.8. CPU Idle và Gantt Segment

- Khi không có tiến trình sẵn sàng, timeline phải có segment `Idle` đến Arrival
  Time gần nhất tiếp theo.
- Hai segment liền kề của cùng một PID phải được gộp thành một segment.
- Segment phải có `end > start`.

## 6. Kết quả và công thức chỉ số

Với mỗi tiến trình:

```text
Completion Time (CT) = thời điểm tiến trình hoàn thành
Turnaround Time (TAT) = CT - AT
Waiting Time (WT) = TAT - BT
Response Time (RT) = thời điểm chạy lần đầu - AT
```

Kết quả tổng hợp gồm:

- Average Waiting Time.
- Average Turnaround Time.
- Average Response Time.
- Context Switch Count.

Context switch chỉ được tính khi CPU chuyển giữa hai PID thực khác nhau. Các
segment `Idle` không được tính là một PID trong phép đếm context switch.

## 7. Model dữ liệu

### 7.1. Model đầu vào và kết quả

- `Process`: dữ liệu tiến trình đã xác thực.
- `GanttSegment`: PID, thời điểm bắt đầu và kết thúc.
- `ProcessMetrics`: CT, TAT, WT, RT của một tiến trình.
- `ScheduleResult`: tên thuật toán, Gantt segments, metrics và các giá trị trung
  bình.
- `ComparisonRow`: dữ liệu so sánh Priority với FCFS cho API tương thích.

### 7.2. Model simulation

- `ReadySnapshot`: trạng thái một tiến trình trong Ready Queue.
- `SimulationStep`: một khoảng thực thi và sự kiện tại bước đó.
- `SimulationRun`: `ScheduleResult` cùng toàn bộ các bước simulation.
- `AlgorithmComparison`: tên và kết quả của một thuật toán trong comparison.

Các model sử dụng dataclass bất biến để UI không sửa ngược dữ liệu thuật toán.

## 8. Contract tám module cố định

Tên và vị trí các module sau là cố định, không được đổi. Thuật toán hoặc chức
năng bổ sung phải đặt trong `service/misc`.

| Module | Trách nhiệm và API chính |
|---|---|
| `module1_nhaplieu.py` | Parse, xác thực và chuẩn hóa input qua `tao_tien_trinh`, `tu_mapping`, `chuan_hoa_danh_sach` |
| `module2_nonpreemptive.py` | Adapter Priority Non-Preemptive; trả `SimulationRun` hoặc `ScheduleResult` |
| `module3_preemptive.py` | Adapter Priority Preemptive; trả `SimulationRun` hoặc `ScheduleResult` |
| `module4_aging.py` | Tính Effective Priority qua `tinh_priority_hieu_dung` |
| `module5_bangketqua.py` | Cung cấp dữ liệu render trung lập và component tự render |
| `module6_ganttchart.py` | `TimelineGanttCanvas` và `ComparisonGanttCanvas` |
| `module7_fcfs.py` | Adapter FCFS và API mapping tương thích source cũ |
| `module8_mainui.py` | Cửa sổ Tkinter Demo V2 và điều phối interaction |

Engine dùng chung nằm tại `service/misc/scheduling.py`. Engine hỗ trợ các khóa:

```text
fcfs
sjf
srtf
priority_non_preemptive
priority_preemptive
round_robin
```

## 9. Hai contract render của Module 5

Module 5 bắt buộc cung cấp hai cách sử dụng độc lập:

### 9.1. Data-render contract

`build_result_view_data(result)` trả dữ liệu trung lập gồm:

- `algorithm`
- `summary`
- `metrics[]` với PID, AT, BT, PR, CT, TAT, WT và RT

Main UI phải sử dụng contract này để tự render Final Metrics.

### 9.2. Self-render contract

`ResultPanel` và `render_result_panel(master, result)` phải tự dựng summary,
Gantt Chart và bảng metrics. Contract này dùng khi cần nhúng kết quả vào một UI
Tkinter khác mà không phụ thuộc Main UI.

## 10. Trạng thái và sự kiện simulation

Simulation có thể phát sinh các sự kiện:

- `CPU IDLE`
- `START`
- `EXEC`
- `NEW ARRIVAL / EXEC`
- `PREEMPTED`
- `FINISHED` hoặc sự kiện kết hợp với `FINISHED`
- `TIME SLICE START`
- `QUANTUM EXPIRED`

Mỗi bước phải ghi rõ khoảng `start → end`, PID đang chạy, snapshot Ready Queue
và nội dung giải thích quyết định lập lịch.

## 11. Yêu cầu giao diện

- Giữ phong cách Tkinter hiện tại và bố cục Demo V2.
- Cửa sổ mặc định có kích thước `1280x900`, tối thiểu `1080x760`.
- Process Input dùng chung cho hai tab.
- Mọi combobox lựa chọn cố định phải ở trạng thái `readonly`.
- Dữ liệu bảng phải căn giữa và có heading rõ ràng.
- Gantt Chart phải phân biệt `Idle` với các tiến trình.
- Đóng cửa sổ phải dừng các callback playback đang chờ.

## 12. Yêu cầu phi chức năng

- Chạy bằng Python 3.13 trở lên.
- Không có dependency pip bắt buộc; Tkinter thuộc bản cài Python trên Windows.
- Không sử dụng global Python để cài package cho dự án.
- Môi trường mặc định nằm tại `D:\HDH\Priority\.venv`.
- Không commit `.venv`, cache hoặc secret.
- Logic thuật toán không được phụ thuộc trực tiếp vào Tkinter.
- UI chỉ điều phối và render; model và engine phải có thể test độc lập.

## 13. Khởi chạy và kiểm thử

Tạo môi trường và chạy ứng dụng:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

Chạy toàn bộ test:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## 14. Tiêu chí nghiệm thu

Hệ thống đạt yêu cầu khi:

1. Input không hợp lệ hoặc PID trùng bị từ chối với thông báo rõ ràng.
2. Detail Simulation chỉ hiển thị `Priority` và `FCFS` trong danh sách thuật
   toán.
3. Cả hai Priority Mode đều chạy được và Aging chỉ ảnh hưởng Priority.
4. Simulation thể hiện đúng Ready Queue, event, CPU và Gantt theo từng bước.
5. Final Metrics chứa đủ mọi PID từ Process Input của lần Prepare hiện tại.
6. Các công thức CT, TAT, WT và RT cho kết quả nhất quán với Gantt Chart.
7. Comparison luôn tạo đúng năm kết quả trên cùng input.
8. Round Robin tuân thủ quantum và thứ tự FIFO.
9. Module 5 hoạt động được ở cả chế độ data-render và self-render.
10. Entry point `main.py` dựng được cửa sổ Demo V2.
11. Toàn bộ test tự động pass trong `.venv` Python 3.13.

## 15. Ngoài phạm vi

- Lưu dữ liệu vào database.
- Đăng nhập hoặc phân quyền người dùng.
- Đồng bộ qua mạng.
- Thay thế scheduler thật của hệ điều hành.
