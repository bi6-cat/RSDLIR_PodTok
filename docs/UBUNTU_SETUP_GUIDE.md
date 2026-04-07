# Hướng Dẫn Cài Đặt và Chạy Trên Ubuntu (Local GPU NVIDIA)

Tài liệu này dành riêng cho việc thiết lập môi trường chạy dự án PodTok trên máy tính cá nhân sử dụng hệ điều hành Ubuntu Linux và có card đồ hoạ NVIDIA (VD: RTX 5060).

## 1. Cài đặt các gói hệ thống cốt lõi
Mở terminal và chạy lệnh sau để tải các công cụ máy chủ:
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv ffmpeg git build-essential rustc cargo
```
*(Ghi chú: `ffmpeg` bắt buộc phải có để script cắt và đọc file audio. `rustc` và `cargo` dùng để build một số thư viện lõi của tokenizer).*

## 2. Tạo môi trường ảo và cài Python Packages
Khởi tạo và kích hoạt môi trường ảo `.venv` ngay trong thư mục dự án:
```bash
python3 -m venv .venv
source .venv/bin/activate
```
Cài đặt toàn bộ thư viện:
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

## 3. KHAI BÁO THƯ VIỆN ĐỘNG CUDA (SỬA LỖI FASTER-WHISPER)
**⚠️ RẤT QUAN TRỌNG:** 
Khi chạy mô hình AI (VD: `faster-whisper`), hệ thống Ubuntu mặc định không biết tìm các thư viện lõi toán học ma trận của Nvidia (`libcublas.so.12`, `libcudnn`) ở đâu dù đã cài qua pip. Bạn sẽ gặp lỗi `RuntimeError: Library libcublas.so.12 is not found...`.

**Cách khắc phục:**
Chạy lệnh này trong terminal (lúc đang bật `.venv`) ĐỂ TRỎ ĐƯỜNG DẪN ẢO TRƯỚC KHI CHẠY SCRIPT:
```bash
export LD_LIBRARY_PATH=`python3 -c 'import nvidia.cublas.lib; import nvidia.cudnn.lib; print(nvidia.cublas.lib.__path__[0] + ":" + nvidia.cudnn.lib.__path__[0])'`
```

**MẸO GHI NHẬN VĨNH VIỄN (Chỉ làm 1 lần):**
Để không phải gõ lại lệnh trên mỗi khi bật máy lại hoặc mở terminal mới, hãy chạy lệnh dưới đây để lưu thẳng cấu hình đó vào file khởi động `.bashrc` của Ubuntu:
```bash
echo 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:'$(python3 -c 'import nvidia.cublas.lib; import nvidia.cudnn.lib; print(nvidia.cublas.lib.__path__[0] + ":" + nvidia.cudnn.lib.__path__[0])') >> ~/.bashrc
source ~/.bashrc
```

## 4. Chạy Bóc Băng Lời Thoại AI
Sau khi đã export đường dẫn CUDA thành công, hãy chạy kịch bản bóc băng:
```bash
python src/data_processing/transcriber.py
```
Lúc này card NVIDIA (Compute) sẽ được bung xõa 100% công suất để chạy AI streaming thời gian thực!