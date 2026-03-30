import struct

class Student:
    # Format struct: 8s (chuỗi 8 byte), 50s (chuỗi 50 byte), i (số nguyên 4 byte)
    # Tổng cộng: 8 + 50 + 4 = 62 bytes / 1 record
    RECORD_FORMAT = '=8s 50s i'
    RECORD_SIZE = struct.calcsize(RECORD_FORMAT)

    def __init__(self, mssv: str, name: str, gender: int):
        self.mssv = mssv
        self.name = name
        self.gender = gender # 0: Nam, 1: Nữ

    def to_bytes(self) -> bytes:
        # Encode sang utf-8. Cắt bớt nếu quá dài, và độn thêm byte null (\x00) nếu bị ngắn
        # Bắt buộc phải làm thế này để giữ đúng 62 bytes cho mọi sinh viên
        mssv_bytes = self.mssv.encode('utf-8')[:8].ljust(8, b'\x00')
        
        # Tiếng Việt có dấu tốn nhiều byte hơn, nên cứ cắt ở 50
        name_bytes = self.name.encode('utf-8')[:50].ljust(50, b'\x00')
        
        # Đóng gói thành nhị phân
        return struct.pack(self.RECORD_FORMAT, mssv_bytes, name_bytes, self.gender)

    @classmethod
    def from_bytes(cls, data: bytes):
        if not data or len(data) != cls.RECORD_SIZE:
            return None
            
        unpacked = struct.unpack(cls.RECORD_FORMAT, data)
        
        # Decode và xóa các byte null bị độn thêm lúc ghi
        mssv = unpacked[0].decode('utf-8').rstrip('\x00')
        name = unpacked[1].decode('utf-8').rstrip('\x00')
        gender = unpacked[2]
        
        return cls(mssv, name, gender)

    def __str__(self):
        gioi_tinh_str = "Nam" if self.gender == 0 else "Nữ"
        return f"{self.mssv} | {self.name} | {gioi_tinh_str}"