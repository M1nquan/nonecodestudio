import os
import sys

# Đảm bảo thư mục hiện tại nằm trong đường dẫn tìm kiếm của Python
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    # ⚠️ THAY 'ten_module' BẰNG TÊN THỰC TẾ CỦA FILE .pyd (Không viết đuôi .pyd)
    # Ví dụ: nếu file của bạn là cheatcs2.pyd thì viết là: import cheatcs2
    import main

    print("[+] Đã import thành công file .pyd!")
    
    # Kiểm tra các hàm và thuộc tính có sẵn bên trong module .pyd
    print("Các thành phần có sẵn:", dir(main))

    # ⚠️ GỌI HÀM BÊN TRONG MODULE (Thay 'ten_ham' bằng hàm thực tế của bạn)
    # Ví dụ: ten_module.start()
    if hasattr(main, 'start'):
        main.start()
    else:
        print("[-] Không tìm thấy hàm 'start' trong module này.")

except ImportError as e:
    print(f"[-] Lỗi: Không thể import file .pyd. Chi tiết: {e}")
except Exception as e:
    print(f"[-] Lỗi trong quá trình thực thi: {e}")