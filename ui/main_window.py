import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from core.models import Student

class MainWindow:
    def __init__(self, root, db, btree):
        self.root = root
        self.db = db          # Nhận StorageEngine
        self.btree = btree    # Nhận BTree
        self.root.title("Hệ Quản Trị CSDL Mini & B-Tree")
        self.root.geometry("1200x750")
        
        self.default_font = ("Segoe UI", 10)
        self.root.option_add("*Font", self.default_font)

        self.create_widgets()
        
        # MÓC NÚT BẤM VÀO HÀM XỬ LÝ 
        self.btn_add.config(command=self.handle_add_student)
        self.btn_search.config(command=self.handle_search_student)
        self.btn_del.config(command=self.handle_delete_student)
        self.load_initial_data()

    def create_widgets(self):
        # SIDEBAR TRÁI: CHỨA INPUT & NÚT BẤM
        # Dùng màu nền xám nhạt (#ecf0f1) để tách biệt với khu vực dữ liệu
        sidebar = tk.Frame(self.root, width=280, bg="#ecf0f1", padx=15, pady=15)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False) # Ép sidebar giữ nguyên chiều rộng 280px

        tk.Label(sidebar, text="QUẢN LÝ SINH VIÊN", font=("Segoe UI", 14, "bold"), bg="#ecf0f1", fg="#2c3e50").pack(pady=(0, 20))

        # Form nhập liệu
        tk.Label(sidebar, text="Mã số sinh viên:", bg="#ecf0f1").pack(anchor=tk.W)
        self.entry_mssv = ttk.Entry(sidebar)
        self.entry_mssv.pack(fill=tk.X, pady=(0, 10))

        tk.Label(sidebar, text="Họ và tên:", bg="#ecf0f1").pack(anchor=tk.W)
        self.entry_name = ttk.Entry(sidebar)
        self.entry_name.pack(fill=tk.X, pady=(0, 10))

        tk.Label(sidebar, text="Giới tính:", bg="#ecf0f1").pack(anchor=tk.W)
        self.combo_gender = ttk.Combobox(sidebar, values=["Nam", "Nữ"], state="readonly")
        self.combo_gender.current(0)
        self.combo_gender.pack(fill=tk.X, pady=(0, 20))

        # Khu vực nút bấm
        tk.Label(sidebar, text="BẢNG ĐIỀU KHIỂN", font=("Segoe UI", 11, "bold"), bg="#ecf0f1", fg="#7f8c8d").pack(anchor=tk.W, pady=(10, 5))
        
        # Trang trí nút bấm bằng ttk.Style
        style = ttk.Style()
        style.configure("Action.TButton", font=("Segoe UI", 10, "bold"), padding=6)

        self.btn_add = ttk.Button(sidebar, text="✚ Thêm sinh viên", style="Action.TButton")
        self.btn_add.pack(fill=tk.X, pady=5)
        
        self.btn_del = ttk.Button(sidebar, text="✖ Xóa theo MSSV", style="Action.TButton")
        self.btn_del.pack(fill=tk.X, pady=5)
        
        self.btn_search = ttk.Button(sidebar, text="🔍 Tìm theo MSSV", style="Action.TButton")
        self.btn_search.pack(fill=tk.X, pady=5)

        # MAIN AREA PHẢI: HIỂN THỊ DỮ LIỆU & B-TREE
        main_area = tk.Frame(self.root, padx=15, pady=15, bg="#ffffff")
        main_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Bảng dữ liệu gốc (Nửa trên)
        db_frame = tk.LabelFrame(main_area, text=" Dữ liệu trong Ổ cứng (.dat) ", font=("Segoe UI", 10, "bold"), bg="#ffffff", fg="#2980b9")
        db_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(0, 10))

        columns = ("mssv", "name", "gender", "offset") # Thêm cột Offset
        self.tree_db = ttk.Treeview(db_frame, columns=columns, show="headings", height=6)
        self.tree_db.heading("mssv", text="MSSV")
        self.tree_db.heading("name", text="Họ tên")
        self.tree_db.heading("gender", text="Giới tính")
        self.tree_db.heading("offset", text="Vị trí (Offset)")
        
        self.tree_db.column("mssv", width=120, anchor=tk.CENTER)
        self.tree_db.column("name", width=250, anchor=tk.W)
        self.tree_db.column("gender", width=100, anchor=tk.CENTER)
        self.tree_db.column("offset", width=100, anchor=tk.CENTER)
        self.tree_db.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Không gian vẽ B-Tree (Nửa dưới)
        btree_frame = tk.LabelFrame(main_area, text=" Chỉ mục B-Tree (Lưu trên RAM) ", font=("Segoe UI", 10, "bold"), bg="#ffffff", fg="#27ae60")
        btree_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(0, 10))

        # THÊM THANH CUỘN NGANG
        self.scrollbar_x = ttk.Scrollbar(btree_frame, orient=tk.HORIZONTAL)
        self.scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Móc Canvas với thanh cuộn (xscrollcommand)
        self.canvas = tk.Canvas(btree_frame, bg="#fdfdfd", highlightthickness=1, highlightbackground="#bdc3c7", xscrollcommand=self.scrollbar_x.set)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Cấu hình thanh cuộn điều khiển trục X của Canvas
        self.scrollbar_x.config(command=self.canvas.xview)
        # -----------------------------------------

        # Nhật ký hoạt động (Dưới cùng)
        log_frame = tk.Frame(main_area, bg="#ffffff")
        log_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        tk.Label(log_frame, text="Nhật ký hệ thống:", font=("Segoe UI", 9, "bold"), bg="#ffffff", fg="#7f8c8d").pack(anchor=tk.W)
        
        # Dùng font Consolas
        self.text_log = tk.Text(log_frame, height=5, bg="#f8f9fa", font=("Consolas", 10), state=tk.DISABLED, relief=tk.FLAT, highlightthickness=1, highlightbackground="#bdc3c7")
        self.text_log.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

    def log_message(self, message):
        self.text_log.config(state=tk.NORMAL)
        self.text_log.insert(tk.END, f"> {message}\n")
        self.text_log.see(tk.END)
        self.text_log.config(state=tk.DISABLED)

    def handle_add_student(self):
        # Lấy dữ liệu từ form
        mssv = self.entry_mssv.get().strip()
        name = self.entry_name.get().strip()
        gender_str = self.combo_gender.get()

        # Check xem có nhập thiếu không
        if not mssv or not name:
            messagebox.showwarning("Lỗi nhập liệu", "Vui lòng nhập đầy đủ MSSV và Họ tên!")
            return
        
        # Check xem MSSV có bị trùng trong B-Tree không
        offset_check, _ = self.btree.search(mssv)
        if offset_check is not None:
            messagebox.showerror("Lỗi logic", f"MSSV {mssv} đã tồn tại trong hệ thống!")
            return

        # Tạo object Sinh viên
        gender_val = 0 if gender_str == "Nam" else 1
        sv = Student(mssv, name, gender_val)

        # Ghi xuống ổ cứng lấy offset
        new_offset = self.db.insert_student(sv)

        # Gắn vào cây B-Tree
        self.btree.insert(mssv, new_offset)

        # Đẩy lên bảng hiển thị (UI)
        self.tree_db.insert("", tk.END, values=(mssv, name, gender_str, new_offset))

        self.redraw_btree()

        # Ghi log báo thành công
        self.log_message(f"Thêm thành công: {mssv} - {name} (Lưu tại Offset: {new_offset})")

        # Xóa trắng form để tiện nhập người tiếp theo
        self.entry_mssv.delete(0, tk.END)
        self.entry_name.delete(0, tk.END)
        self.entry_mssv.focus() # Tự động nháy con trỏ chuột vào lại ô MSSV

    def handle_search_student(self):
        mssv = self.entry_mssv.get().strip()
        
        if not mssv:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập MSSV cần tìm!")
            return
            
        # Gọi hàm search của B-Tree (trả về offset và danh sách các node đã đi qua)
        offset, path = self.btree.search(mssv)
        
        if offset is not None:
            # Kêu Canvas vẽ lại cây, truyền cái path vào để nó Highlight
            self.redraw_btree(highlight_path=path)
            self.log_message(f"Tìm thấy MSSV {mssv} tại Offset {offset}. Đã làm nổi bật đường duyệt cây!")
            
            # Tự động bôi đen dòng đó trong Bảng dữ liệu
            for item in self.tree_db.get_children():
                if self.tree_db.item(item, "values")[0] == mssv:
                    self.tree_db.selection_set(item)
                    self.tree_db.see(item)
                    break
        else:
            # Không tìm thấy thì vẽ lại cây bình thường (tẩy highlight cũ)
            self.redraw_btree(highlight_path=[]) 
            self.log_message(f"Không tìm thấy sinh viên có MSSV {mssv}!")

    def handle_delete_student(self):
        mssv = self.entry_mssv.get().strip()
        
        # Kiểm tra input rỗng
        if not mssv:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập MSSV cần xóa!")
            return
            
        # Tìm thử xem sinh viên có tồn tại không
        offset, _ = self.btree.search(mssv)
        if offset is None:
            messagebox.showerror("Không tìm thấy", f"Hệ thống không có sinh viên mang MSSV {mssv}!")
            return
            
        # Hỏi xác nhận người dùng
        confirm = messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa sinh viên MSSV {mssv} không?\nHành động này không thể hoàn tác.")
        if not confirm:
            return

        # Xóa khỏi cấu trúc B-Tree
        try:
            self.btree.delete(mssv)
        except AttributeError:
            messagebox.showerror("Lỗi hệ thống", "Có vẻ như bạn chưa cài đặt hàm delete() trong file btree.py!")
            return
        except Exception as e:
            messagebox.showerror("Lỗi khi xóa", f"Đã xảy ra lỗi khi xóa trong B-Tree: {e}")
            return
        self.db.delete_student(offset)

        # Xóa khỏi bảng hiển thị (Treeview)
        for item in self.tree_db.get_children():
            if self.tree_db.item(item, "values")[0] == mssv:
                self.tree_db.delete(item)
                break

        # Cập nhật lại giao diện
        self.redraw_btree()
        self.log_message(f"✖ Đã xóa thành công sinh viên MSSV: {mssv}")

        # Xóa trắng form nhập liệu
        self.entry_mssv.delete(0, tk.END)
        self.entry_name.delete(0, tk.END)

    def redraw_btree(self, highlight_path=None):
        self.canvas.delete("all")
        if not self.btree.root.keys:
            return
            
        self.highlight_path = highlight_path if highlight_path else []
            
        self.canvas.update_idletasks()
        
        # Tăng base width lên 2000 để khi khởi tạo cây có không gian rộng, 
        # dãn ra hai bên và kích hoạt thanh cuộn nếu vượt quá kích thước màn hình
        canvas_width = max(2000, self.canvas.winfo_width()) 
        
        self._draw_node(self.btree.root, x=canvas_width / 2, y=40, dx=canvas_width / 2.5)
        
        # CẬP NHẬT VÙNG CUỘN
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def _draw_node(self, node, x, y, dx):
        text = " | ".join(node.keys)
        # Giảm chiều rộng tối thiểu của hộp xuống 60px cho các Node thon gọn
        box_width = max(60, len(text) * 9) 
        box_height = 30
        
        x1, y1 = x - box_width / 2, y - box_height / 2
        x2, y2 = x + box_width / 2, y + box_height / 2
        
        is_highlighted = node in self.highlight_path
        
        if not node.leaf:
            num_children = len(node.children)
            start_x = x - dx * (num_children - 1) / 2
            
            for i, child in enumerate(node.children):
                child_x = start_x + i * dx
                child_y = y + 70
                
                start_line_x = x1 + (i + 1) * (box_width / (num_children + 1))
                
                is_child_highlighted = child in self.highlight_path
                line_color = "#e74c3c" if (is_highlighted and is_child_highlighted) else "#7f8c8d"
                line_width = 3 if line_color == "#e74c3c" else 2
                
                self.canvas.create_line(start_line_x, y2, child_x, child_y - box_height / 2, fill=line_color, width=line_width)
                
                # Hệ số thu hẹp dx ở các tầng dưới thành chia 2.5 
                # Đảm bảo các nhánh con bó sát vào cha chúng hơn
                self._draw_node(child, child_x, child_y, dx / 2.5)

        box_fill = "#fcf3cf" if is_highlighted else "#d5f5e3"
        box_outline = "#f39c12" if is_highlighted else "#27ae60"
        text_fill = "#d35400" if is_highlighted else "#196f3d"

        if self.highlight_path and not is_highlighted:
            box_fill = "#f4f6f6"
            box_outline = "#bdc3c7"
            text_fill = "#95a5a6"

        self.canvas.create_rectangle(x1, y1, x2, y2, fill=box_fill, outline=box_outline, width=2)
        self.canvas.create_text(x, y, text=text, font=("Segoe UI", 9, "bold"), fill=text_fill)

    def load_initial_data(self):
        # Đọc toàn bộ dữ liệu từ ổ cứng và xây dựng lại cây B-Tree, cập nhật UI
        
        try:
            all_records = self.db.get_all_students() 
            
            if not all_records:
                self.log_message("Hệ thống khởi động: Không có dữ liệu cũ.")
                return

            for record in all_records:
                # Bóc tách dữ liệu
                mssv, name, gender_val, offset = record
                gender_str = "Nam" if gender_val == 0 else "Nữ"

                # Gắn vào B-Tree
                self.btree.insert(mssv, offset)

                # Đẩy lên bảng (Treeview)
                self.tree_db.insert("", tk.END, values=(mssv, name, gender_str, offset))

            # Xây xong thì vẽ lại cây
            self.redraw_btree()
            self.log_message(f"Khởi động thành công: Đã khôi phục {len(all_records)} bản ghi từ ổ cứng!")
            
        except AttributeError:
            messagebox.showwarning("Thiếu hàm", "Class Database của bạn chưa có hàm đọc toàn bộ dữ liệu (ví dụ: get_all_students)!")
        except Exception as e:
            messagebox.showerror("Lỗi khôi phục", f"Lỗi khi đọc file .dat: {e}")