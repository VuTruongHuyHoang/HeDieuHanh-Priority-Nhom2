# Prompt tạo bộ CSV mặc định cho bài toán lập lịch CPU

## Vai trò

Bạn là kỹ sư dữ liệu đang tạo bộ dữ liệu mặc định để kiểm thử và phân tích các thuật toán lập lịch CPU gồm FCFS, Priority Non-Preemptive, Priority Preemptive và Aging.

## Mục tiêu

Dùng Python trong môi trường phân tích dữ liệu để tạo một file ZIP chứa 100 file CSV hợp lệ. Bộ dữ liệu sẽ được dùng để khảo sát ảnh hưởng của aging interval đến Waiting Time, Turnaround Time, Response Time, Context Switch và nguy cơ starvation.

Không in toàn bộ nội dung của 100 file CSV ra hội thoại. Hãy tạo file thật và cung cấp liên kết tải file ZIP.

## Cấu hình chung

- `RANDOM_SEED = 20260820`.
- Tổng số CSV: `100`.
- Mỗi CSV có số process ngẫu nhiên từ `30` đến `70`, bao gồm cả 30 và 70.
- Tên process phải duy nhất trong từng file: `P1`, `P2`, ..., `Pn`.
- Header bắt buộc và đúng thứ tự:

```csv
PID,AT,BT,PR
```

- `AT`, `BT` và `PR` phải là số nguyên.
- `AT >= 0`.
- `BT > 0`.
- `PR >= 0`.
- Trong dự án này, giá trị `PR` càng nhỏ thì độ ưu tiên càng cao.
- Mỗi file phải có ít nhất một process với `AT = 0`.
- Mỗi file phải có ít nhất một process thuộc nhóm ưu tiên cao, `PR` từ 0 đến 2.
- Mỗi file phải có ít nhất một process thuộc nhóm ưu tiên thấp, `PR` từ 7 đến 9.
- Không tạo cột index.
- Không có ô trống, PID trùng hoặc dòng sai định dạng.
- Lưu CSV bằng UTF-8.
- Sắp xếp các dòng theo `AT` tăng dần; nếu `AT` bằng nhau thì sắp theo số thứ tự của PID.
- Có thể điều chỉnh một vài giá trị sau khi random để thỏa các điều kiện bắt buộc như `AT = 0` hoặc đủ hai nhóm priority, nhưng không được lựa chọn dataset dựa trên kết quả của thuật toán lập lịch.
- Không chạy thuật toán lập lịch rồi loại bỏ hoặc tạo lại dataset chỉ để làm cho Aging tốt hơn FCFS.

## Phân nhóm dữ liệu

Chia 100 file thành đúng 5 nhóm, mỗi nhóm 20 file.

### 1. `uniform`

- `AT` random đều từ 0 đến 80.
- `BT` random đều từ 1 đến 20.
- `PR` random đều từ 0 đến 9.
- Dùng làm nhóm dữ liệu cơ bản.

### 2. `high_contention`

- `AT` random từ 0 đến 15 để nhiều process vào ready queue gần nhau.
- `BT` random từ 3 đến 20.
- `PR` random từ 0 đến 9.
- Dùng để kiểm tra khi hệ thống có tải cao.

### 3. `starvation_pressure`

- Chọn ngẫu nhiên khoảng 20% đến 30% process làm nhóm ưu tiên thấp:
  - `AT` từ 0 đến 10.
  - `BT` từ 8 đến 20.
  - `PR` từ 7 đến 9.
- Các process còn lại:
  - `AT` từ 5 đến 100.
  - `BT` từ 1 đến 12.
  - `PR` từ 0 đến 4.
- Nhóm này mô phỏng các process ưu tiên thấp đến sớm nhưng liên tục gặp process ưu tiên cao đến sau.
- Các giá trị vẫn phải được random theo seed; không được gán trước kết quả thuật toán.

### 4. `mixed_burst`

- `AT` random từ 0 đến 70.
- Khoảng 75% process có `BT` từ 1 đến 5.
- Khoảng 25% process có `BT` từ 12 đến 30.
- `PR` random từ 0 đến 9.
- Dùng để kiểm tra sự pha trộn giữa process ngắn và dài.

### 5. `clustered_arrival`

- Chọn `AT` quanh các cụm thời gian 0, 10, 25 và 45.
- Với mỗi process, chọn ngẫu nhiên một tâm cụm rồi cộng độ lệch ngẫu nhiên từ -3 đến 3.
- Sau khi cộng độ lệch, `AT` không được nhỏ hơn 0.
- `BT` random từ 1 đến 20.
- `PR` random từ 0 đến 9.
- Dùng để mô phỏng process xuất hiện theo từng đợt.

## Quy tắc đặt tên

Đặt tên tuần tự và kèm tên scenario:

```text
data/default_dataset/dataset_001_uniform.csv
...
data/default_dataset/dataset_020_uniform.csv
data/default_dataset/dataset_021_high_contention.csv
...
data/default_dataset/dataset_040_high_contention.csv
data/default_dataset/dataset_041_starvation_pressure.csv
...
data/default_dataset/dataset_060_starvation_pressure.csv
data/default_dataset/dataset_061_mixed_burst.csv
...
data/default_dataset/dataset_080_mixed_burst.csv
data/default_dataset/dataset_081_clustered_arrival.csv
...
data/default_dataset/dataset_100_clustered_arrival.csv
```

## Quy tắc đường dẫn

- Không hardcode ổ đĩa, tên người dùng hoặc đường dẫn tuyệt đối.
- Không ghi bất kỳ đường dẫn riêng của máy tạo dữ liệu vào CSV, manifest, README hoặc script.
- Mọi đường dẫn bên trong ZIP phải là đường dẫn tương đối.
- Cấu trúc ZIP phải bắt đầu từ thư mục `data/`.
- Người dùng phải có thể giải nén ZIP tại thư mục gốc của bất kỳ bản sao dự án nào.
- Thư mục cần chọn trong MainUI sau khi giải nén là đường dẫn tương đối `data/default_dataset` tính từ thư mục gốc dự án.

Cấu trúc bắt buộc bên trong ZIP:

```text
data/
├── default_dataset/
│   ├── dataset_001_uniform.csv
│   ├── ...
│   └── dataset_100_clustered_arrival.csv
├── default_dataset_manifest.json
└── default_dataset_README.md
```

Không đặt manifest, báo cáo hoặc README dạng CSV trong `data/default_dataset`, vì ứng dụng sẽ đọc toàn bộ file `.csv` trong thư mục này như dữ liệu process.

## Manifest

Tạo file `data/default_dataset_manifest.json` chứa:

- `random_seed`.
- `total_files`.
- `total_processes`.
- `min_processes_per_file`.
- `max_processes_per_file`.
- Số file của từng scenario.
- Danh sách từng file, mỗi phần tử gồm:
  - `filename`: đường dẫn tương đối tính từ thư mục `data/default_dataset`.
  - `scenario`.
  - `process_count`.
  - `min_at`.
  - `max_at`.
  - `min_bt`.
  - `max_bt`.
  - `min_pr`.
  - `max_pr`.
  - `sha256` của file CSV.

## README

Tạo `data/default_dataset_README.md` mô tả ngắn gọn:

- Mục đích của bộ dữ liệu.
- Ý nghĩa của `PID`, `AT`, `BT` và `PR`.
- Quy ước `PR` nhỏ hơn nghĩa là độ ưu tiên cao hơn.
- Năm nhóm scenario và mục đích của từng nhóm.
- Random seed đã sử dụng.
- Thư mục tương đối cần chọn trong MainUI: `data/default_dataset`.
- Lưu ý rằng bộ dữ liệu được tạo độc lập với kết quả mô phỏng, không bảo đảm Aging luôn tốt hơn FCFS.

## Kiểm tra bắt buộc trước khi hoàn thành

Dùng Python để kiểm tra lại toàn bộ artifact sau khi tạo:

1. Có đúng 100 file CSV trong `data/default_dataset`.
2. Có đúng 20 file cho mỗi scenario.
3. Mỗi file có từ 30 đến 70 dòng dữ liệu, không tính header.
4. Header của mọi file chính xác là `PID,AT,BT,PR`.
5. Mỗi dòng có đúng bốn cột.
6. PID không trùng trong cùng file.
7. Tất cả `AT`, `BT`, `PR` là số nguyên và đúng miền giá trị.
8. Mỗi file có ít nhất một `AT = 0`, một `PR` từ 0 đến 2 và một `PR` từ 7 đến 9.
9. Không có hai file có toàn bộ nội dung giống nhau; kiểm tra bằng SHA-256.
10. Tổng process trong manifest khớp tổng process thực tế.
11. Tên file, scenario và số lượng trong manifest khớp file thực tế.
12. Đọc lại toàn bộ CSV bằng Python `csv` module và xác nhận không có lỗi.
13. File ZIP giữ đúng cấu trúc thư mục tương đối và không chứa absolute path.

Nếu có kiểm tra thất bại, sửa artifact và chạy lại toàn bộ validation trước khi trả lời. Không trả file ZIP chưa đạt đủ các điều kiện trên.

## Đầu ra

- Tạo file tải xuống có tên `priority_default_dataset.zip`.
- ZIP phải chứa đúng cấu trúc bắt đầu từ `data/` như đã mô tả.
- Không in toàn bộ dữ liệu CSV trong câu trả lời.
- Trả về liên kết tải file ZIP.
- Kèm báo cáo ngắn gồm:
  - Số CSV.
  - Tổng số process.
  - Số process nhỏ nhất và lớn nhất trong một file.
  - Số file theo từng scenario.
  - Random seed.
  - Kết quả validation.
  - Thư mục tương đối cần chọn trong MainUI: `data/default_dataset`.

## Phương án dự phòng

Nếu môi trường hiện tại không thể tạo file ZIP để tải xuống, không in nội dung của 100 CSV ra hội thoại. Thay vào đó, tạo và cung cấp một file duy nhất tên `generate_default_dataset.py` có thể chạy độc lập để sinh toàn bộ dữ liệu và file ZIP theo đúng yêu cầu trên.

Script dự phòng phải:

- Chỉ dùng Python standard library.
- Nhận tham số tùy chọn `--output-root`.
- Dùng thư mục hiện tại làm giá trị mặc định của `--output-root`.
- Xác định đường dẫn bằng `pathlib`, theo nguyên tắc:

```python
project_root = Path(args.output_root).resolve()
dataset_directory = project_root / "data" / "default_dataset"
```

- Có thể chạy từ thư mục gốc dự án bằng:

```text
python generate_default_dataset.py --output-root .
```

- Không chứa bất kỳ đường dẫn tuyệt đối hoặc đường dẫn riêng của một máy cụ thể.
- Tự tạo dataset, manifest, README, chạy validation và tạo `priority_default_dataset.zip`.
- Nếu validation thất bại, thoát với mã lỗi khác 0 và mô tả lỗi rõ ràng.

Hoàn thành khi file ZIP tải được và toàn bộ validation đều đạt, hoặc khi phương án dự phòng đã cung cấp được script Python hoàn chỉnh có cùng tiêu chí thành công.
