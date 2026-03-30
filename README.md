# Hệ Quản Trị CSDL đơn giản

Dự án mô phỏng cơ chế hoạt động của một hệ quản trị cơ sở dữ liệu. Ứng dụng sử dụng cấu trúc B-Tree để quản lý chỉ mục trên RAM và file nhị phân để lưu trữ dữ liệu vật lý.

## Cấu trúc dự án

* `core/`: Chứa các module xử lý logic nền tảng (cấu trúc B-Tree, định dạng bản ghi, thao tác đọc/ghi file).
* `ui/`: Chứa mã nguồn xây dựng giao diện người dùng (Tkinter).
* `data/`: Thư mục chứa file dữ liệu vật lý `student_db.dat` (tự động tạo khi chạy).
* `main.py`: Tệp thực thi chính của ứng dụng.

## Tính năng kỹ thuật

* **Thêm bản ghi:** Ghi nối dữ liệu (append) kích thước cố định (62 bytes) vào cuối file `.dat` và nạp khóa vào B-Tree.
* **Tìm kiếm:** Định vị offset của bản ghi qua B-Tree và đọc trực tiếp từ ổ cứng.
* **Xóa bản ghi (Soft Delete):** Xóa node trên B-Tree và ghi đè byte Null (`\x00`) tại vị trí offset trong file vật lý (Tombstone).
* **Khôi phục dữ liệu:** Tự động quét file nhị phân và xây dựng lại cây chỉ mục khi khởi động ứng dụng.

## Yêu cầu môi trường

* Hệ điều hành: Windows / macOS / Linux
* Ngôn ngữ: Python 3.x
* Thư viện: `tkinter`, `struct`, `os` (tích hợp sẵn trong Python, không cần cài đặt thêm).

## Hướng dẫn sử dụng

1. Tải mã nguồn về máy tính.
2. Mở Terminal hoặc Command Prompt tại thư mục dự án.
3. Chạy lệnh sau để khởi động phần mềm:
   `python main.py`
