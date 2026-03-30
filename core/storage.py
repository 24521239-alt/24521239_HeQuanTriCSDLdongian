import os
from .models import Student

class StorageEngine:
    def __init__(self, filepath='data/student_db.dat'):
        self.filepath = filepath
        # Đảm bảo thư mục và file luôn tồn tại trước khi thao tác
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        if not os.path.exists(self.filepath):
            open(self.filepath, 'wb').close()

    def insert_student(self, student: Student) -> int:
        # Ghi sinh viên mới vào cuối file, trả về offset để lưu vào B-Tree
        # Mở mode 'a+b': append + binary
        with open(self.filepath, 'a+b') as f:
            # Di chuyển con trỏ xuống cuối file
            f.seek(0, os.SEEK_END)
            # Vị trí con trỏ lúc này chính là offset của bản ghi mới
            offset = f.tell() 
            f.write(student.to_bytes())
            return offset

    def read_student(self, offset: int) -> Student:
        # Nhảy thẳng tới offset và đọc ra 62 bytes
        # Mở mode 'rb': read binary
        with open(self.filepath, 'rb') as f:
            f.seek(offset)
            data = f.read(Student.RECORD_SIZE)
            return Student.from_bytes(data)
        
    def get_all_students(self):
        # Quét toàn bộ file .dat và trả về danh sách sinh viên cùng offset của họ.
        all_records = []
        if not os.path.exists(self.filepath):
            return all_records

        with open(self.filepath, 'rb') as f:
            offset = 0
            while True:
                data = f.read(Student.RECORD_SIZE)
                
                if not data or len(data) != Student.RECORD_SIZE:
                    break
                
                # Nếu đọc lên toàn byte Null thì bỏ qua (sinh viên đã bị xóa)
                if data == b'\x00' * Student.RECORD_SIZE:
                    offset += Student.RECORD_SIZE
                    continue
                
                student = Student.from_bytes(data)
                if student and student.mssv:
                    all_records.append((student.mssv, student.name, student.gender, offset))
                
                offset += Student.RECORD_SIZE
                
        return all_records
    
    def delete_student(self, offset: int):
        # Nhảy đến đúng offset trong file .dat và ghi đè 62 bytes Null để xóa vật lý
        if not os.path.exists(self.filepath):
            return
            
        # Mở mode 'r+b' (read + write binary): Cho phép ghi đè mà không làm hỏng file
        with open(self.filepath, 'r+b') as f:
            f.seek(offset)
            # Ghi đè 62 bytes trống (b'\x00') lên vị trí cũ
            f.write(b'\x00' * Student.RECORD_SIZE)