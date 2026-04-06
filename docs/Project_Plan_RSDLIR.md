# KẾ HOẠCH THỰC HIỆN DỰ ÁN CHI TIẾT (PROJECT EXECUTION PLAN)
**Dự án:** PodBite / PodTok – Nền tảng Khám phá Podcast Ngắn (12 Tuần)

Kế hoạch này được chia thành 6 Phase (Giai đoạn) với phương pháp quản lý Agile. Kế hoạch định rõ công việc từng tuần để team dễ dàng phân chia task (Backend, AI/ML, Frontend).

---

## Phase 1: Setup Môi trường & Crawl Dữ liệu (Tuần 1 - 2)
**Mục tiêu:** Có kho dữ liệu Podcast thô và thiết lập xong kiến trúc rỗng.

*   **Tuần 1: Khởi tạo Project & Docs**
    *   Tạo GitHub Repository chung, setup Rule commit.
    *   Setup môi trường Python (`conda` hoặc `venv`), tạo file `requirements.txt`.
    *   Setup Docker Compose chứa: MongoDB, Redis, Milvus (Vector DB).
*   **Tuần 2: Thu thập Dữ liệu (Crawler)**
    *   Lập danh sách 5 kênh YouTube/RSS uy tín (Ví dụ: Vietcetera, Spiderum...).
    *   Viết script tự động dùng `yt-dlp` tải khoảng 100 tập Podcast (định dạng mp3/m4a, 16kHz).
    *   Lưu thông tin Metadata gốc (Tác giả, Tiêu đề bài dài) vào MongoDB.

---

## Phase 2: Xây dựng Offline ML Pipeline (Tuần 3 - 4)
**Mục tiêu:** Xử lý toàn bộ audio thô thành các mẩu 30s chứa Subtitle và Embeddings.

*   **Tuần 3: Phân rã Audio & Speech-to-Text**
    *   Tích hợp VAD (`pyannote.audio`) để nhận diện tiếng người, loại bỏ khoảng lặng/nhạc.
    *   Cắt các đoạn âm thanh từ 30s đến 45s, tránh cắt giữa câu. Lưu file audio nhỏ lên thư mục Storage/MinIO.
    *   Đẩy các đoạn audio ngắn qua mô hình `Whisper` để lấy Text (Subtitle) + Word timestamps.
*   **Tuần 4: Trích xuất Đặc trưng (Embeddings) & VectorDB**
    *   Truyền Text vừa có vào `PhoBERT/BERT` $\rightarrow$ sinh Text Vector (768d).
    *   Truyền Audio vào `Wav2Vec 2.0` $\rightarrow$ sinh Emotion/Audio Vector (256d/768d).
    *   Hợp nhất (Concat) thành Multi-modal Vector.
    *   Viết script đẩy toàn bộ List Vectors vào **Milvus** / **FAISS**.

---

## Phase 3: Mô phỏng Dữ liệu & Train SASRec Model (Tuần 5 - 6)
**Mục tiêu:** Có một mô hình AI Recommender System có khả năng sinh dự đoán mượt mà.

*   **Tuần 5: Sinh Dữ liệu Giả lập (Synthetic Data)**
    *   User thật chưa có, viết script Python sinh ra kịch bản của 500 "User ảo".
    *   Tạo các logs hành vi nghe: Ví dụ User A thích khoa học (nghe full 30s các clip khoa học, skip clip tình cảm < 3s).
    *   Lưu log này vào CSV (user_id, item_id, dwell_time, skip_or_not) để làm dataset huấn luyện.
*   **Tuần 6: Huấn luyện kiến trúc SASRec**
    *   Code Model kiến trúc Transformer-based (SASRec) bằng PyTorch.
    *   Đưa dữ liệu Session của User ảo vào Train. Tùy chỉnh Loss (Binary Cross-entropy).
    *   Đánh giá model bằng các chỉ số Offline: HR@10 (Hit Rate), NDCG@10. Lưu model dạng `model.pth`.

---

## Phase 4: Phát triển Backend API (Tuần 7 - 8)
**Mục tiêu:** Xây dựng cầu nối giữa Mobile App và các Mô hình AI.

*   **Tuần 7: CRUD & Redis Queue**
    *   Khởi tạo dự án `FastAPI`. Viết API `/auth` để tạo Guest Session.
    *   Tích hợp Redis. Viết API `/track` để App liên tục gửi hành vi lướt (item_id, dwell_time). Khi gọi API này, Backend update mảng Session trên Redis.
*   **Tuần 8: Recommend API & Semantic Search**
    *   Viết API `/feed`: Lấy chuỗi lịch sử từ Redis $\rightarrow$ Load model `model.pth` chạy inference $\rightarrow$ Lấy Vector kết quả $\rightarrow$ Query Milvus lấy Top 10 Audio ID tiếp theo $\rightarrow$ Trả JSON về cho App.
    *   Viết API `/search`: Query text tự do, dùng PhoBERT encode text $\rightarrow$ Query Milvus.

---

## Phase 5: Xây dựng Giao diện Mobile App (Tuần 9 - 10)
**Mục tiêu:** Ứng dụng điện thoại mượt mà, UX cuộn dọc như TikTok.

*   **Tuần 9: Dựng Layout & Audio Player**
    *   Khởi tạo Project Flutter (hoặc React Native).
    *   Sử dụng thư viện `just_audio` hoặc `audioplayers`. Cấu hình preload để cuộn không bị khựng/loading.
    *   Dựng UI màn hình trang chủ (Full màn hình, Nút Like, Share bên phải).
*   **Tuần 10: Tích hợp API & Animation**
    *   Nối API `/feed` vào luồng lướt. Viết bộ lắng nghe (Timer) đếm ngược số giây người dùng dừng lại ở clip $\rightarrow$ tự động gọi API `/track` khi người ta lướt sang clip khác.
    *   Xử lý file Subtitle (VTT), chạy chữ highlight dạng karaoke khớp với Audio.

---

## Phase 6: Tích hợp Toàn hệ thống, Test & Viết Báo Cáo (Tuần 11 - 12)
**Mục tiêu:** Hoàn thiện sản phẩm cuối cùng và slide bảo vệ.

*   **Tuần 11: End-to-end Testing & Refactor**
    *   Chạy thử hệ thống thực tế trên nhiều điện thoại. Kiểm tra tốc độ phản hồi từ lúc vuốt đến lúc load audio mới (Latency < 300ms là đạt).
    *   Bắt các lỗi crash App, lỗi VectorDB overload.
    *   Quay Video luồng trải nghiệm App hoạt động mượt mà.
*   **Tuần 12: Viết quyển Báo cáo & Slide**
    *   Xuất các biểu đồ Loss của SASRec, độ chính xác ASR của Whisper.
    *   Đóng quyển Báo cáo, vẽ lại các biểu đồ Architecture/User Flow.
    *   Chuẩn bị Slide trình bày đồ án (Có các dẫn chứng về tính cấp thiết + Demo).

---
*Ghi chú: Team nên chia việc theo các cột dọc (Ví dụ: Bạn A làm Pipeline AI ở Phase 2,3; Bạn B làm Backend Phase 4; Bạn C làm Flutter Phase 5). Các Phase có thể bắt đầu gối đầu lên nhau (Ví dụ Phase 5 bắt đầu code UI chay ngay từ Tuần 4).*