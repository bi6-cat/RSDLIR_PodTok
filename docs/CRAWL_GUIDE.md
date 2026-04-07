# Hướng Dẫn Cào Dữ Liệu Podcast (Data Ingestion)

Thư mục `src/data_ingestion` chứa các kịch bản (scripts) để tải âm thanh từ nhiều nguồn xử lý khác nhau. Dưới đây là hướng dẫn chi tiết cho từng luồng (Flow) tải dữ liệu.

---

## Luồng 1: Tải audio từ kênh/playlist YouTube 
Sử dụng khi bạn muốn tải âm thanh từ các kênh YouTube hoặc Playlist.

1. Mở file `data/1_youtube_urls.txt` và dán các link YouTube vào (mỗi link 1 dòng).
2. Chạy lệnh:
   ```bash
   python src/data_ingestion/1_youtube_crawler.py
   ```
3. **Kết quả:** Các file audio `.mp3` sẽ được lưu vào `data/raw_audio/`.

---

## Luồng 2: Tìm Apple Podcasts $\rightarrow$ Lọc $\rightarrow$ Tải 
Sử dụng khi bạn muốn tìm kênh theo từ khóa, nhưng muốn kiểm tra lại danh sách các podcast trước khi quyết định tải về máy cục bộ.

1. **Bước A: Tìm kiếm và trích xuất link**
   - Mở file `data/2_3_apple_keywords.txt` và nhập các từ khóa chủ đề (VD: tâm lý học, kinh tế...).
   - Chạy lệnh:
     ```bash
     python src/data_ingestion/2a_apple_build_link_sheet.py
     ```
   - **Kết quả:** Sinh ra file Excel/CSV tại `data/2_apple_podcast_links.csv`.

2. **Bước B: Lọc nội dung (Tùy chọn)**
   - Mở file `data/2_apple_podcast_links.csv` bằng Excel hoặc VS Code.
   - Xóa bỏ các dòng (tập podcast) mà bạn KHÔNG muốn tải. Lưu lại.

3. **Bước C: Tải âm thanh hàng loạt**
   - Chạy lệnh:
     ```bash
     python src/data_ingestion/2b_apple_download_from_sheet.py
     ```
   - **Kết quả:** Tải toàn bộ mp3 trong CSV về thư mục `data/raw_audio_mass/`.

---

## Luồng 3: Tải Apple Podcasts Tự Động 100%
Sử dụng khi bạn muốn chương trình tự động lấy keyword $\rightarrow$ tự tìm podcast hot $\rightarrow$ tự tải mp3 mà không cần lọc qua file CSV.

1. Mở file `data/2_3_apple_keywords.txt` và nhập các từ khóa.
2. Chạy lệnh:
   ```bash
   python src/data_ingestion/3_apple_auto_discover_download.py
   ```
3. **Kết quả:** Audio tự động tuôn thẳng về `data/raw_audio_mass/`.

---

## Luồng 4: Tải trực tiếp qua file RSS thuần
Sử dụng khi bạn LÀM RÕ được link cấp nguồn (RSS - file `.xml`) của một podcast bất kỳ. Cực kỳ nhanh để test data mẫu.

1. Mở file `data/4_rss_links.txt` và gắn link nguồn XML của podcast vào.
2. Chạy lệnh:
   ```bash
   python src/data_ingestion/4_direct_rss_fetcher.py
   ```
3. **Kết quả:** Tải mp3 về `data/raw_audio/`.

---
**💡 Cấu trúc thư mục kết quả sinh ra:**
- `data/raw_audio/`: Chứa file âm thanh của luồng 1 và 4.
- `data/raw_audio_mass/`: Chứa số lượng lớn file âm thanh của luồng 2 và 3.
- `data/podcasts_metadata.json` (hoặc `mass_podcasts_metadata.json`): Chứa toàn bộ thông tin về tên tác giả, tiêu đề, ID file... để dùng cho các bước AI phía sau.
