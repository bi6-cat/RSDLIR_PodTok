# Hướng Dẫn Chạy Kịch Bản Trên Google Colab (Qua Git)

Colab là môi trường miễn phí cực kì lý tưởng vì tốc độ mạng siêu nhanh và có sẵn GPU cho AI (Whisper). Dưới đây là cách đưa toàn bộ mã nguồn từ GitHub lên Colab và chạy.

## Bước 1: Khởi tạo Notebook & Kết nối Google Drive
Mô trường của Colab sẽ tự động bị xóa sau ngắt kết nối. Bạn **bắt buộc** phải kết nối Google Drive để lưu vĩnh viễn các file Audio và Subtitle tải về.

Mở 1 file Notebook (`.ipynb`) mới trên [Google Colab](https://colab.research.google.com/) và dán đoạn code sau vào 1 cell (ô code) đầu tiên, rồi ấn chạy:

```python
from google.colab import drive
drive.mount('/content/drive')
```
*(Trình duyệt sẽ hiện popup yêu cầu bạn cấp quyền truy cập Drive, hãy bấm Allow).*

## Bước 2: Clone (Kéo) mã nguồn từ GitHub về Drive
Tạo một ô code mới (Cell) và dán đoạn sau vào để tải project về lưu vào thư mục `Colab Notebooks` trong Drive của bạn:

```bash
# Di chuyển tới thư mục an toàn trên Drive của bạn
%cd /content/drive/MyDrive/

# Kéo mãng nguồn từ Github về Drive (Chỉ chạy 1 lần duy nhất)
# Thay YOUR_GITHUB_REPO_LINK bằng link git của bạn (VD: https://github.com/Username/RSDLIR_PodTok.git)
!git clone <YOUR_GITHUB_REPO_LINK>

# Di chuyển con trỏ làm việc vào trong thư mục dự án vừa tải về trên Drive
%cd /content/drive/MyDrive/RSDLIR_PodTok
```

**💡 LƯU Ý QUAN TRỌNG VỀ LƯU TRỮ TRÊN DRIVE:** 
Bởi vì bạn đã dùng lệnh `%cd /content/drive/MyDrive/RSDLIR_PodTok` để chỉ định thư mục làm việc hiện tại đang nằm trên **Google Drive** của bạn, nên **TẤT CẢ** các file Code tạo ra (file `.txt`, `.csv`, `.mp3` dung lượng lớn, file text `.json` bóc băng) đều sẽ được script Python **đọc và lưu mặc định trực tiếp vào Google Drive** của bạn bên trong thư mục `RSDLIR_PodTok/data/`. Bạn không cần phải chỉnh sửa dòng code Python nào cả!

## Bước 3: Cài đặt thư viện cần thiết
Tạo ô code (Cell) mới và dán vào:

```bash
# Cập nhật pip và cài đặt toàn bộ package theo yêu cầu
!pip install --upgrade pip
!pip install -r requirements.txt

# (Tuỳ chọn) Colab thường đã có sẵn ffmpeg, nhưng cài thêm cho chắc cũng không rớt mạng
!apt-get install -y ffmpeg
```

## Bước 4: Chỉnh sửa file data cấu hình ngay trên Colab
Bạn KHÔNG cần mở code editor phức tạp. Colab có màn hình quản lý file ở cạnh trái:
1. Bạn nhìn sang **cột bên trái** màn hình Colab, bấm vào icon **Folder (Tìm kiếm tệp)**.
2. Điều hướng vào thư mục `drive/MyDrive/RSDLIR_PodTok/data/config/`.
3. Nháy đúp vào các file Text như `1_youtube_urls.txt`, `2_3_apple_keywords.txt`... để chỉnh sửa link/từ khoá.
4. Nhấn `Ctrl + S` (hoặc `Cmd + S`) để lưu ngay trên trình duyệt colab.

## Bước 5: Chạy các kịch bản Cào Data (Ingestion)
Mỗi lúc muốn chạy kịch bản nào, bạn chỉ cần tạo 1 cell mới và gọi lệnh python như sau:

**Ví dụ cào từ YouTube:**
```bash
!python src/data_ingestion/1_youtube_crawler.py
```

**Ví dụ cào tự động Apple Podcast:**
```bash
!python src/data_ingestion/3_apple_auto_discover_download.py
```

## Bước 6: Chạy AI Whisper tách lời thoại (Processing)
Nếu bạn có GPU trên Colab, tốc độ sẽ nhanh hơn hàng chục lần so với máy tính thường.
*(Để bật GPU trên Colab: Menu `Runtime` > `Change runtime type` > Chọn `T4 GPU` hoặc `V100 GPU`).*

```bash
!python src/data_processing/transcriber.py
```

---
🎉 **Thành quả:** Bất cứ khi nào Colab báo rớt mạng hoặc tắt trình duyệt, đừng lo, toàn bộ code, file âm thanh (`.mp3`) và file văn bản (`.json`) đều đã được lưu chặt trên Google Drive cá nhân của bạn!