class BTreeNode:
    def __init__(self, is_leaf=True):
        self.leaf = is_leaf
        self.keys = []      # Chứa mảng MSSV (Ví dụ: ['24521239', '24521233'])
        self.offsets = []   # Chứa mảng Offset tương ứng (Ví dụ: [0, 64])
        self.children = []  # Chứa các BTreeNode con

class BTree:
    def __init__(self):
        self.root = BTreeNode(is_leaf=True)

    def search(self, mssv):
        # Hàm tìm kiếm, trả về offset và 'đường đi' để vẽ UI
        return self._search_node(self.root, mssv, path=[])

    def _search_node(self, node, mssv, path):
        path.append(node) # Lưu lại node đã đi qua
        
        # Tìm vị trí khóa đầu tiên lớn hơn hoặc bằng mssv cần tìm
        i = 0
        while i < len(node.keys) and mssv > node.keys[i]:
            i += 1
        
        # Nếu tìm thấy đúng MSSV
        if i < len(node.keys) and node.keys[i] == mssv:
            return node.offsets[i], path
        
        # Nếu không thấy mà lại là node lá (cụt đường) -> Không tồn tại
        if node.leaf:
            return None, path
            
        # Nếu chưa tới lá, chui xuống node con nhánh thứ i để tìm tiếp
        return self._search_node(node.children[i], mssv, path)

    def insert(self, mssv, offset):
        # Hàm thêm dữ liệu vào cây
        # Gọi hàm đệ quy chèn từ gốc
        res = self._insert_node(self.root, mssv, offset)
        
        # res khác None tức là Gốc cũ đã bị tràn và nứt ra, nó ném lên 1 khóa giữa
        if res is not None:
            promoted_key, promoted_offset, right_node = res
            
            # Tạo gốc mới cao hơn để chứa khóa bị đẩy lên
            new_root = BTreeNode(is_leaf=False)
            new_root.keys = [promoted_key]
            new_root.offsets = [promoted_offset]
            new_root.children = [self.root, right_node]
            self.root = new_root # Cập nhật gốc mới

    def _insert_node(self, node, mssv, offset):
        # Hàm đệ quy chèn dữ liệu và xử lý tách node nếu tràn
        # Tìm vị trí để nhét vào node hiện tại
        i = 0
        while i < len(node.keys) and mssv > node.keys[i]:
            i += 1
            
        if node.leaf:
            # Nếu là node lá, nhét thẳng tay vào mảng
            node.keys.insert(i, mssv)
            node.offsets.insert(i, offset)
        else:
            # Nếu là node cành, phải chui xuống con để nhét
            res = self._insert_node(node.children[i], mssv, offset)
            if res is not None:
                # Thằng con ở dưới bị tràn, nó đẩy lên 1 khóa mới và 1 cục node phải
                p_key, p_offset, right_child = res
                node.keys.insert(i, p_key)
                node.offsets.insert(i, p_offset)
                node.children.insert(i + 1, right_child)
        
        # Kiểm tra xem nhét xong node có bị quá tải không
        # Max chỉ được 2. Nếu = 3 là phải chẻ đôi.
        if len(node.keys) > 2:
            mid_idx = 1 # Khóa nằm giữa (index 1) sẽ bị đẩy lên trên
            p_key = node.keys[mid_idx]
            p_offset = node.offsets[mid_idx]
            
            # Tạo node mới chứa nửa bên phải
            right_node = BTreeNode(is_leaf=node.leaf)
            right_node.keys = node.keys[mid_idx+1:]
            right_node.offsets = node.offsets[mid_idx+1:]
            
            # Gọt lại node hiện tại thành nửa bên trái
            node.keys = node.keys[:mid_idx]
            node.offsets = node.offsets[:mid_idx]
            
            # Nếu có con thì cũng phải chia lại con cho 2 bên
            if not node.leaf:
                right_node.children = node.children[mid_idx+1:]
                node.children = node.children[:mid_idx+1]
                
            # Trả về khóa giữa và node phải cho cha nó xử lý
            return p_key, p_offset, right_node
        
        # Trả về None báo hiệu nhét êm xuôi, không bị tràn
        return None
    
    def delete(self, mssv):
        # Hàm công khai để gọi từ UI
        if not self.root.keys:
            return # Cây rỗng

        self._delete(self.root, mssv)

        # Nếu gốc bị mất hết khóa (do gộp node kéo từ cha xuống) nhưng vẫn có con,
        # ta cắt bỏ gốc cũ, cho thằng con đầu tiên lên làm gốc mới.
        if len(self.root.keys) == 0 and not self.root.leaf:
            self.root = self.root.children[0]

    def _delete(self, node, mssv):
        # Hàm đệ quy xử lý xóa và cân bằng lại cây
        i = 0
        while i < len(node.keys) and mssv > node.keys[i]:
            i += 1

        # TRƯỜNG HỢP 1: TÌM THẤY MSSV TRONG NODE HIỆN TẠI
        if i < len(node.keys) and node.keys[i] == mssv:
            if node.leaf:
                # 1a. Nếu là node lá: Cứ thế xóa thẳng tay
                node.keys.pop(i)
                node.offsets.pop(i)
            else:
                # 1b. Nếu là node cành: Phải tìm node "thế mạng"
                # Ta mượn phần tử lớn nhất của nhánh con bên trái 
                pred_node = node.children[i]
                while not pred_node.leaf:
                    pred_node = pred_node.children[-1]
                
                pred_key = pred_node.keys[-1]
                pred_offset = pred_node.offsets[-1]

                # Ráp node thế mạng vào vị trí hiện tại
                node.keys[i] = pred_key
                node.offsets[i] = pred_offset

                # Đệ quy xuống nhánh trái để xóa phần tử vừa bị đem đi thế mạng
                self._delete(node.children[i], pred_key)
                
                # Kiểm tra xem xóa xong nhánh con đó có bị "đói" không
                self._fix_underflow(node, i)
        
        # TRƯỜNG HỢP 2: CHƯA TÌM THẤY, ĐI TIẾP XUỐNG CON ĐỂ TÌM
        else:
            if node.leaf:
                # Chui xuống tận lá rồi mà vẫn không thấy -> MSSV không tồn tại
                return
            
            self._delete(node.children[i], mssv)
            # Tương tự, đi lên từ đệ quy phải xem thằng con có bị "đói" không
            self._fix_underflow(node, i)

    def _fix_underflow(self, parent, child_idx):
        # Hàm cứu trợ khi một node con bị mất sạch khóa (len = 0)
        child = parent.children[child_idx]
        if len(child.keys) > 0:
            return # Node vẫn còn khóa, sống tốt, không cần cứu!

        # CHIẾN THUẬT 1: Mượn anh em bên trái (nếu anh em trái giàu - có >1 khóa)
        if child_idx > 0 and len(parent.children[child_idx - 1].keys) > 1:
            left_sibling = parent.children[child_idx - 1]
            # 1. Kéo khóa của cha rớt xuống cho con
            child.keys.insert(0, parent.keys[child_idx - 1])
            child.offsets.insert(0, parent.offsets[child_idx - 1])
            # 2. Đẩy khóa lớn nhất của anh em trái lên thay vị trí cho cha
            parent.keys[child_idx - 1] = left_sibling.keys.pop(-1)
            parent.offsets[child_idx - 1] = left_sibling.offsets.pop(-1)
            # 3. Chuyển giao đàn con (nếu có)
            if not left_sibling.leaf:
                child.children.insert(0, left_sibling.children.pop(-1))

        # CHIẾN THUẬT 2: Mượn anh em bên phải (nếu anh em phải giàu - có >1 khóa)
        elif child_idx < len(parent.children) - 1 and len(parent.children[child_idx + 1].keys) > 1:
            right_sibling = parent.children[child_idx + 1]
            child.keys.append(parent.keys[child_idx])
            child.offsets.append(parent.offsets[child_idx])
            
            parent.keys[child_idx] = right_sibling.keys.pop(0)
            parent.offsets[child_idx] = right_sibling.offsets.pop(0)
            
            if not right_sibling.leaf:
                child.children.append(right_sibling.children.pop(0))

        # CHIẾN THUẬT 3: Hàng xóm cũng nghèo, đành phải GỘP NODE
        else:
            if child_idx > 0:
                # Gộp với anh em bên trái
                left_sibling = parent.children[child_idx - 1]
                # Kéo khóa của cha xuống ráp vào
                left_sibling.keys.append(parent.keys.pop(child_idx - 1))
                left_sibling.offsets.append(parent.offsets.pop(child_idx - 1))
                # Gom nốt tàn dư (nếu có)
                left_sibling.keys.extend(child.keys)
                left_sibling.offsets.extend(child.offsets)
                if not child.leaf:
                    left_sibling.children.extend(child.children)
                # Khai tử thằng con rỗng
                parent.children.pop(child_idx)
            else:
                # Gộp với anh em bên phải (do child_idx == 0 không có anh em trái)
                right_sibling = parent.children[child_idx + 1]
                child.keys.append(parent.keys.pop(child_idx))
                child.offsets.append(parent.offsets.pop(child_idx))
                
                child.keys.extend(right_sibling.keys)
                child.offsets.extend(right_sibling.offsets)
                if not right_sibling.leaf:
                    child.children.extend(right_sibling.children)
                # Khai tử anh em phải
                parent.children.pop(child_idx + 1)