# TÀI LIỆU PIPELINE HỌC SÁU (ML PIPELINE)
**Dự án:** PodBite / PodTok

Tài liệu này mô tả chi tiết pipeline thu thập, xử lý dữ liệu và huấn luyện các mô hình AI/ML trong dự án.

---

## 1. Pipeline Tiền Xử Lý Âm Thanh (Audio Preprocessing)

### Bước 1.1: Ingestion (Thu thập gốc)
*   **Công cụ:** `yt-dlp`
*   **Nguồn:** Danh sách kênh YouTube (Vietcetera, Tri Kỷ Cảm Xúc, Spiderum, The Present Writer).
*   **Định dạng tải về:** Cấu hình trích xuất tệp `.m4a` hoặc `.mp3`, Sample rate: `16 kHz` (chuẩn đầu vào tốt nhất cho Whisper và Wav2Vec), Mono channel.

### Bước 1.2: Phân đoạn (Segmentation / Chunking)
*   **Công cụ:** `FFmpeg` (Pre-cut), `pyannote.audio` (cho Voice Activity Detection - VAD) và `librosa` / `pydub`.
*   **Quy trình:**
    1.  **Pre-cut Tối ưu (Core Segment Extraction):** Áp dụng thuật toán nhảy cóc tránh Intro/Ads để lấy 10 phút phần "Lõi" (Core) có giá trị cao nhất:
        * Dưới 10 phút: Giữ nguyên.
        * Từ 10 - 45 phút: Bỏ qua 1/3 thời lượng đầu. (VD: Podcast 30 phút -> Cắt từ 10:00 -> 20:00).
        * Lớn hơn 45 phút: Quảng cáo, chitchat cùng lắm kéo dài 15 phút. Bỏ qua cứng 15 phút đầu. (VD: Podcast 2h -> Cắt từ 15:00 -> 25:00).
        Việc này giúp LLM và Whisper bám trúng ngay vào phần Deep Talk, loại bỏ hoàn toàn các reel lỗi có nội dung chào hỏi.
    2.  Dạy VAD quét trên file 10 phút này để loại bỏ khoảng lặng dài > 2 giây và nhạc nền không có tiếng người.
    3.  Dùng Whisper lấy timestamps thô.
    4.  Dựa vào dấu câu cuối dấy (dấu chấm, phẩy), cắt audio thành các đoạn ngắn (Reel) có độ dài ngẫu nhiên từ `30s đến 45s`.

---

## 2. Pipeline Trích Xuất Đặc Trưng (Feature Extraction)

### Bước 2.1: Text & Transcript (Whisper + PhoBERT)
1.  **Whisper (OpenAI):** Xử lý đoạn audio 30s. Xuất ra Transcript (văn bản) + Word-level Timestamps (để làm hiệu ứng karaoke trên Mobile).
2.  **PhoBERT (VinAI):** Truyền Transcript vào PhoBERT để lấy `Text Embedding Vector` (Kích thước: 768 chiều).

### Bước 2.2: Speech Emotion & Energy (Wav2Vec 2.0)
1.  **Wav2Vec 2.0 (Facebook/Meta):** Truyền nguyên audio 30s vào mô hình Wav2Vec 2.0 (đã fine-tune trên dữ liệu âm thanh cảm xúc - SER).
2.  **Đầu ra:** Phân loại nhãn cảm xúc (Vui, Buồn, Bình Tĩnh, Năng lượng cao) + Truy xuất `Audio/Emotion Embedding Vector` từ các layer ẩn (Kích thước: 768 hoặc bổ sung giảm chiều PCA xuống 256).

### Bước 2.3: Multi-modal Fusion (Hợp nhất)
*   **Phương pháp:** Nối hai véc-tơ lại với nhau (Concatenation).
*   Công thức: $v_{final} = [v_{text\_768} \oplus v_{audio\_256}]$
*   Kết quả thu được 1 véc-tơ ngữ nghĩa - âm thanh kích thước 1024 chiều. Lưu véc-tơ này cùng với `segment_id` vào Milvus / FAISS.

---

## 3. Pipeline Hệ Thống Gợi Ý (Recommender System - SASRec)

### Bước 3.1: Định nghĩa Bài toán (Session-based)
*   **Sequential Problem:** Người dùng nghe $S_1 \rightarrow S_2 \rightarrow S_3...$. Dự đoán đoạn audio tiếp theo $S_{next}$ người dùng sẽ không bấm Skip.
*   **Implicit Feedback:** Thay vì Ratings 1-5 sao, hệ thống dùng Dwell-Time (thời gian nghe):
    *   Nghe < 3s: Phạt (Negative implicit).
    *   Nghe > 15s hoặc Bấm Like/Chuyển bài dài: Thưởng (Positive implicit).

### Bước 3.2: Dữ liệu Huấn luyện Giả lập (Synthetic Data)
Do chưa có user thật, ta sẽ dùng Python Script tạo ra tập Data gồm 10,000 phiên (sessions):
*   **User Persona 1:** Thích nghe "Self-help tâm lý lười biếng", lướt nhanh các audio chủ đề khác.
*   **User Persona 2:** Thích nghe "Công nghệ blockchain", skip các chủ đề tình yêu.
*   Log giả lập ghi ra file CSV: `user_id, session_id, segment_id, dwell_time, timestamp`.

### Bước 3.3: Kiến trúc SASRec (Self-Attention)
*   **Mô hình:** Dựa trên Transformer Architecture (BERT cho RecSys).
*   **Bản chất:** Mô hình dùng cơ chế Self-attention để đánh trọng số sự liên quan của các item người dùng vừa nghe trong cùng 1 phiên. (Ví dụ: đoạn audio $S_3$ có ảnh hưởng mạnh từ đoạn $S_1$ hơn là $S_2$).
*   **Loss Function:** Binary Cross Entropy (BCE) Loss (Phân biệt giữa Positive Item thực sự và Negative Samples được lấy ngẫu nhiên).
*   **Cold-Start Strategy:** Đối với 5 lần vuốt đầu tiên của một User hoàn toàn mới, sẽ áp dụng Random K-Nearest Neighbors (Content-based) từ kho chủ đề họ chọn lúc Onboarding thay vì dùng SASRec.

---

## 4. Pipeline Triển Khai (Deployment)
1.  Đóng gói Model SASRec qua `ONNX` hoặc `TorchScript` để giảm thời gian inference.
2.  Load model tĩnh trên bộ nhớ FastAPI lúc boot server.
3.  Khi có Request, thực hiện truy xuất Session từ Redis $\rightarrow$ Nạp mảng ID vào SASRec $\rightarrow$ Lấy kết quả $\rightarrow$ Map với FAISS/Milvus $\rightarrow$ Trả về Client.
