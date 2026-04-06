# ĐẶC TẢ API (API SPECIFICATIONS)
**Dự án:** PodBite / PodTok

Tài liệu này mô tả chi tiết các RESTful API giao tiếp giữa Mobile App/Web Frontend và hệ thống Backend (FastAPI).

---

## 1. Init & Authentication (Khởi tạo phiên)

### `POST /api/v1/auth/session`
*   **Mô tả:** Tạo một `session_id` mới cho người dùng khi mở App (kể cả Guest) để phục vụ cho luồng Tracking và Recommend.
*   **Request Body:**
    ```json
    {
      "device_id": "string",
      "user_id": "string (optional - nếu đã login)",
      "initial_topics": ["tech", "psychology", "comedy"] // Dùng cho Cold-start
    }
    ```
*   **Response (200 OK):**
    ```json
    {
      "session_id": "sess_abc123",
      "expires_in": 3600
    }
    ```

---

## 2. Core Features (Feed & Tracking)

### `GET /api/v1/feed/recommendations`
*   **Mô tả:** Lấy danh sách (batch) các đoạn podcast ngắn tiếp theo dựa trên hành vi hiện tại (SASRec inference).
*   **Query Parameters:**
    *   `session_id` (string): Bắt buộc.
    *   `limit` (int): Mặc định là 5.
*   **Response (200 OK):**
    ```json
    {
      "items": [
        {
          "segment_id": "seg_001_1",
          "podcast_title": "Tâm lý học về sự lười biếng",
          "host_name": "Tri Kỷ Cảm Xúc",
          "audio_url": "https://s3.domain.com/audio/seg_001_1.mp3",
          "cover_image": "https://s3.domain.com/images/pod_001.jpg",
          "captions": [
            {"start": 0.0, "end": 2.5, "text": "Sự lười biếng đôi khi"},
            {"start": 2.5, "end": 5.0, "text": "không phải do bạn kém cỏi"}
          ],
          "emotion_tag": "Calm",
          "full_podcast_id": "pod_001"
        }
      ]
    }
    ```

### `POST /api/v1/feed/track`
*   **Mô tả:** Mobile App báo cáo hành vi của người dùng trên mỗi 1 segment (rất quan trọng để cập nhật chuỗi Session trên Redis).
*   **Request Body:**
    ```json
    {
      "session_id": "sess_abc123",
      "segment_id": "seg_001_1",
      "interaction_type": "view", // view | like | share | click_full
      "dwell_time": 15.5, // Số giây nán lại nghe đoạn audio này
      "is_skipped": false // true nếu vuốt qua trước khi hết 3 giây đầu
    }
    ```
*   **Response (200 OK):**
    ```json
    {
      "status": "success",
      "message": "Interaction logged"
    }
    ```

---

## 3. Search & Discovery (Tìm kiếm)

### `GET /api/v1/search/semantic`
*   **Mô tả:** Tìm kiếm ngữ nghĩa tự do. Convert query text thành vector, truy vấn trên Vector Database (Milvus/FAISS).
*   **Query Parameters:**
    *   `query` (string): Text từ người dùng (Vd: "cách vượt qua trì hoãn").
    *   `limit` (int): Mặc định là 10.
*   **Response (200 OK):**
    ```json
    {
      "query": "cách vượt qua trì hoãn",
      "results": [
        {
          "segment_id": "seg_009_3",
          "podcast_title": "Phá vỡ vòng lặp trì hoãn",
          "similarity_score": 0.92,
          "audio_url": "..."
        }
      ]
    }
    ```
