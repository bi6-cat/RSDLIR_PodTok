# BẢN THIẾT KẾ HỆ THỐNG (SYSTEM DESIGN)
**Dự án:** PodBite / PodTok – Nền tảng Khám phá Podcast Ngắn dựa trên AI và Gợi ý Thời gian thực.

---

## 1. Tổng quan Kiến trúc (High-Level Architecture)

Kiến trúc hệ thống được chia làm hai hệ thống chính hoạt động song song để đảm bảo tốc độ phản hồi real-time (<100ms) trên app nhưng vẫn xử lý được khối lượng dữ liệu âm thanh/văn bản lớn:

1. **Online System (Hệ thống Tương tác Thời gian thực):** Chịu trách nhiệm nhận luồng hành vi của người dùng (vuốt, nghe, bỏ qua), cập nhật Session vào bộ nhớ đệm (Redis), chạy mô hình dự đoán (SASRec) và truy vấn Vector DB để trả về âm thanh.
2. **Offline System (Hệ thống Tiền xử lý Dữ liệu):** Chạy ngầm định kỳ (Background Jobs) để crawl dữ liệu Podcast dài, xử lý âm thanh, trích xuất đặc trưng (Text/Emotion) ra Multi-modal Vector và lưu trữ vào Database.

---

## 2. Sơ đồ Kiến trúc Hệ thống (System Architecture Diagram)

\\\mermaid
flowchart TD
    %% Khối Client
    subgraph Client [Client Side]
        App[Mobile App: Flutter/React]
    end

    %% Khối Online Backend
    subgraph Online [Online/Real-time Pipeline - FastAPI]
        API[API Gateway / Controller]
        SessionStore[(Redis Cache<br>User Session)]
        RecEngine[Recommendation Engine<br>SASRec Model]
        SearchEngine[Semantic Search]
    end

    %% Khối Database
    subgraph Storage [Databases]
        MongoDB[(MongoDB<br>Metadata & Logs)]
        VectorDB[(Vector DB<br>Milvus / FAISS)]
        S3[(Object Storage / S3<br>Audio Files)]
    end

    %% Khối Offline AI 
    subgraph Offline [Offline ML Pipeline - Celery/RabbitMQ]
        Crawler[Crawler<br>yt-dlp]
        AudioProc[Audio Processing<br>VAD + Splitter]
        Whisper[Whisper<br>Speech-to-Text]
        Wav2Vec[Wav2Vec 2.0<br>Emotion Extractor]
        BERT[BERT/RoBERTa<br>Text Embedder]
        Fusion[Multi-modal Vector Fusion]
    end

    %% Flow kết nối Online
    App -- "1. Vuốt/Click (Session ID + Action)" --> API
    API -- "2. Lấy/Cập nhật chuỗi hành vi" --> SessionStore
    API -- "3. Truyền chuỗi hành vi" --> RecEngine
    RecEngine -- "4. Sinh Target Vector" --> VectorDB
    VectorDB -- "5. Trả về ID đoạn Audio gần nhất" --> API
    API -- "6. Lấy Metadata & Audio" --> MongoDB
    MongoDB -.-> S3
    API -- "7. Trả Audio Stream & Captions" --> App

    %% Flow tìm kiếm
    App -- "Search Query" --> SearchEngine
    SearchEngine -- "Text-to-Vector" --> BERT
    SearchEngine -- "K-NN Search" --> VectorDB

    %% Flow kết nối Offline
    Crawler --> AudioProc
    AudioProc -- "Audio Chunks 30s" --> S3
    AudioProc --> Whisper
    AudioProc --> Wav2Vec
    Whisper -- "Transcript" --> BERT
    Wav2Vec -- "Emotion Vector" --> Fusion
    BERT -- "Semantic Vector" --> Fusion
    Fusion -- "Insert Vector" --> VectorDB
    Whisper -- "Transcript & Timestamps" --> MongoDB
\\\

---

## 3. Thiết kế Chi tiết các Phân hệ (Component Design)

### 3.1. Phân hệ App Mobile (Client)
*   **Chức năng:** Phát audio dạng cuộn dọc (như TikTok), hiển thị Highlight Captions, gửi Tracking Event (Play, Pause, Skip).
*   **Tracking Timer:** Liên tục do lường **Dwell-time** (số giây nán lại ở mỗi đoạn âm thanh). Nếu < 3s = Negative Feedback (Dislike/Skip). Nếu > 15s = Positive Feedback.
*   **Giao thức:** REST API hoặc gRPC để stream dữ liệu.

### 3.2. Phân hệ Backend (FastAPI)
*   Được chọn vì hỗ trợ Asynchronous (Bất đồng bộ) hiệu năng cao, đặc biệt tốt khi làm việc với các mô hình Machine Learning bằng Python.
*   **Log Ingestor:** Hứng event tracking từ Mobile, đẩy nhanh vào Redis List (lưu giữ chuỗi hành vi trong phiên làm việc).

### 3.3. Phân hệ Recommender System (SASRec)
*   **Self-Attention Sequential Recommendation:** Mô hình học sâu dựa trên kiến trúc Transformer.
*   **Input:** Chuỗi (Sequence) các ID của đoạn audio mà người dùng vừa nghe (lấy từ Redis), mỗi ID được padding với vector ngữ nghĩa và cảm xúc.
*   **Output:** Dự đoán một Vector ảo (Target Vector) đại diện cho sở thích *tiếp theo* của người dùng.

### 3.4. Phân hệ Tiền xử lý Âm thanh (Audio Processing Worker)
Sử dụng Celery worker kết hợp queue (RabbitMQ) để quản lý luồng xử lý:
1.  **VAD (Voice Activity Detection):** Lọc bỏ các đoạn nhạc dạo, tiếng im lặng dài.
2.  **Whisper:** Tạo Subtitles (VTT/SRT). Tìm mốc thời gian phù hợp (ko cắt giữa chừng câu nói) để trích xuất 30-45 giây.
3.  **Wav2Vec / BERT:** Tạo Embeddings nhúng. Véc-tơ tổng hợp (Multi-modal) sẽ là: Concatenate(Text_Vector, Emotion_Vector).

---

## 4. Thiết kế Luồng Dữ liệu (Data Flows)

### 4.1. Luồng Cập nhật Nội dung Sinh tự động (Offline Flow)
1. Crawl/Tải MP3 từ YouTube hoặc RSS Podcast qua yt-dlp.
2. Đẩy vào Queue. Worker lấy audio thô thực hiện chuẩn hóa (128kbps, Mono).
3. Cắt audio thành file nhỏ (chunks), lưu lên S3/MinIO.
4. Chạy mô hình AI trích xuất Caption, Sentiment.
5. Merge (hợp nhất) thành một Vector tổng hợp, Insert vào Milvus VectorDB và MongoDB.

### 4.2. Luồng Khám phá Thời gian thực (Real-time Online Flow)
1. App gửi Log lướt/vuốt: POST /api/v1/track kèm { "session_id": "xxx", "item_id": "A_01", "watch_time": 20 }.
2. Backend update Session hiện tại vào **Redis**.
3. App yêu cầu nội dung mới: GET /api/v1/feed.
4. Backend lấy mảng Session_ID từ Redis, truyền qua **SASRec** Model làm inference (chuẩn đoán).
5. SASRec tạo ra Vector dự đoán (Target Vector).
6. Truy vấn VectorDB bằng Thuật toán lấy lân cận gần nhất (K-NN Search / Cosine Similarity). Trả về Audio_ID phù hợp nhất cho App.

---

## 5. Thiết kế Schema Cơ sở dữ liệu (Database Schema)

### 5.1. MongoDB (Core Metadata)
**Collection podcasts (Chứa thông tin bài gốc):**
\\\json
{
  "_id": "pod_001",
  "title": "Tâm lý học về sự lười biếng",
  "author": "Tri Kỷ",
  "source_url": "youtube.com/..."
}
\\\

**Collection short_segments (Chứa các đoạn cắt ngắn):**
\\\json
{
  "_id": "seg_001_1",
  "podcast_id": "pod_001",
  "start_time": 120.5,
  "end_time": 155.0,
  "audio_url": "s3://bucket/seg_1.mp3",
  "transcript": "Sự lười biếng đôi khi không phải do bạn kém cỏi...",
  "emotion_label": "Calm"
}
\\\

**Collection user_interactions (Log dài hạn train AI):**
\\\json
{
  "user_id": "usr_999",
  "session_id": "sess_11",
  "segment_id": "seg_001_1",
  "dwell_time_seconds": 25,
  "timestamp": "2026-04-06T10:00:00Z"
}
\\\

### 5.2. Redis (Real-time Store)
*   **Key:** session:{session_id}:history
*   **Value:** ["seg_A:30s", "seg_B:2s", "seg_C:15s"]

### 5.3. Vector Database (Milvus / Qdrant)
Mỗi Node Vector gồm:
*   segment_id (Khóa chính map với Mongo)
*   ector (Array[Float32] 1024-Dimension)
