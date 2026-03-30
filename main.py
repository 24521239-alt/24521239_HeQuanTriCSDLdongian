import tkinter as tk
from ui.main_window import MainWindow
from core.storage import StorageEngine
from core.btree import BTree

if __name__ == "__main__":
    # Khởi tạo Backend
    db = StorageEngine()
    btree = BTree()
    
    # Khởi tạo Giao diện và truyền Backend vào
    root = tk.Tk()
    app = MainWindow(root, db, btree) 
    
    app.log_message("Hệ thống khởi động thành công. Đang chờ thao tác...")
    root.mainloop()