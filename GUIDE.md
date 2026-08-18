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

## 6. Chạy kiểm thử

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Kết quả thành công sẽ kết thúc bằng:

```text
OK
```

## 7. Cập nhật source mới nhất

Trước khi bắt đầu làm việc:

```powershell
git switch dev
git pull origin dev
```

Sau khi pull, nếu `requirements.txt` có thay đổi, chạy lại:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 8. Kích hoạt môi trường tùy chọn

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

## 9. Xử lý lỗi thường gặp

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

## 10. Quy trình đầy đủ

Với máy mới, có thể thực hiện lần lượt:

```powershell
git clone -b dev https://github.com/VuTruongHuyHoang/HeDieuHanh-Priority-Nhom2.git
cd HeDieuHanh-Priority-Nhom2
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe main.py
```
