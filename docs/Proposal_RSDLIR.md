# BẢN MÔ TẢ ĐỒ ÁN

## 1. Thông tin chung
* **Tên đề tài (Tiếng Việt):** Xây dựng Nền tảng Khám phá Podcast Ngắn (Short-audio) dựa trên Đặc trưng Đa phương thức và Hành vi Thời gian thực.
* **Tên đề tài (Tiếng Anh):** A Multi-modal and Real-time Session-based Recommendation System for Short-Podcast Discovery.
* **Tên ứng dụng (Dự kiến):** PodBite (hoặc PodTok).
* **Lĩnh vực ứng dụng:** Trí tuệ nhân tạo (AI), Xử lý dữ liệu đa phương thức, Hệ thống gợi ý.

---

## 2. Tóm tắt dự án (Abstract)
Thị trường Podcast đang đối mặt với rào cản "High Commitment" (người dùng lười bắt đầu một tập dài 1-2 tiếng nếu chưa biết nội dung có hay không). Dự án **PodBite** giải quyết bài toán này bằng cách áp dụng phương pháp tiêu thụ nội dung vi mô (Micro-consumption). 

Hệ thống sử dụng các mô hình Deep Learning (Whisper, Wav2Vec 2.0) để tự động trích xuất các đoạn cao trào (30-45 giây) từ Audio gốc, phân tích ngữ nghĩa và cảm xúc giọng nói. Sau đó, một hệ thống gợi ý chuỗi hành vi (SASRec) sẽ học các thao tác vuốt/bỏ qua (skip) của người dùng theo thời gian thực để liên tục thay đổi luồng nội dung tiếp theo, mang lại trải nghiệm khám phá mượt mà tương tự TikTok.

---

## 3. Mục tiêu dự án (Phân rã theo 3 môn học)

### 3.1. Mục tiêu Deep Learning (Trích xuất đặc trưng)
* Sử dụng **Whisper** để thực hiện Speech-to-Text, lấy `timestamps` để cắt ghép âm thanh chuẩn xác và tạo phụ đề tự động (Auto-captions).
* Sử dụng **Wav2Vec 2.0** để phân tích tín hiệu âm thanh thô, nhận diện cảm xúc và mức năng lượng (Speech Emotion Recognition - SER).
* Sử dụng mô hình ngôn ngữ (**BERT/RoBERTa**) để trích xuất véc-tơ ngữ nghĩa từ văn bản (Topic Modeling).

### 3.2. Mục tiêu Recommender System (Cá nhân hóa)
* Xây dựng mô hình **SASRec (Self-Attention Sequential Recommendation)** để dự đoán nội dung tiếp theo dựa trên chuỗi tương tác (session) hiện tại của người dùng.
* Giải quyết bài toán Cold-start bằng phương pháp Content-based Filtering.
* Xử lý phản hồi ngầm định (Implicit Feedback): Phân tích thời gian dừng (Dwell time) và thao tác lướt (Skip) để gán trọng số cho mô hình.

### 3.3. Mục tiêu Information Retrieval (Tra cứu)
* Xây dựng hệ thống tìm kiếm theo ngữ nghĩa (Semantic Search) cho phép người dùng tra cứu Podcast/Host dựa trên từ khóa hoặc văn bản mô tả tự do.
* Lưu trữ và truy vấn hiệu suất cao với cơ sở dữ liệu véc-tơ (**Vector Database**).

---

## 4. Phạm vi dự án (Scope & Limitations)
* **Dữ liệu:** Giới hạn thu thập khoảng 100-200 tập Podcast (tập trung vào top 50 kênh tiếng Việt phổ biến trên YouTube/Spotify).
* **Xử lý:** Chỉ tự động cắt 3-5 đoạn nổi bật nhất trên mỗi tập Podcast để làm dữ liệu huấn luyện.
* **Mô phỏng:** Sử dụng Synthetic Data (dữ liệu giả lập) cho 100-500 user ảo với các kịch bản hành vi khác nhau để chứng minh thuật toán hoạt động.

---

## 5. Kiến trúc hệ thống (System Architecture)

Dự án được chia thành 2 luồng (Pipelines) chính:

**Luồng Xử lý dữ liệu (Offline Pipeline):**
1. **Ingestion:** Tải Audio & Metadata từ YouTube/RSS Feed bằng `yt-dlp`.
2. **Processing:** Voice Activity Detection (VAD) -> Whisper (Transcript + Timestamps) -> Cắt đoạn 30-45s.
3. **Embedding:** Wav2Vec (Emotion Vector) + BERT (Text Vector) -> Hợp nhất thành Multi-modal Vector.
4. **Storage:** Lưu Vector vào Milvus/FAISS, lưu Metadata vào MongoDB.

**Luồng Phục vụ người dùng (Online/Real-time Pipeline):**
1. Người dùng mở App -> Gửi API request lên Backend kèm `Session_ID`.
2. Mô hình SASRec lấy lịch sử "vuốt" hiện tại -> Dự đoán Vector lý tưởng tiếp theo.
3. Khớp Vector dự đoán với Vector Database (IR) để lấy đoạn Audio phù hợp nhất đẩy về App.
4. Người dùng lướt -> Cập nhật log -> Vòng lặp tiếp tục.

---

## 6. Công nghệ sử dụng (Tech Stack)
* **AI/Machine Learning:** Whisper (OpenAI), Wav2Vec 2.0 (Facebook), PhoBERT, SASRec (PyTorch/TensorFlow).
* **Backend API:** Python (FastAPI).
* **Cơ sở dữ liệu:** * `MongoDB`: Lưu Metadata và User Logs.
  * `FAISS / Milvus`: Lưu trữ và truy vấn Vector.
* **Frontend:** Flutter (Mobile) hoặc React (Web Mobile-first).

---

## 7. Kế hoạch thực hiện dự kiến (Timeline - 12 Tuần)
| Thời gian | Hạng mục công việc |
| :--- | :--- |
| **Tuần 1-2** | Thu thập dữ liệu âm thanh, nghiên cứu Whisper & Wav2Vec. |
| **Tuần 3-5** | Code Offline Pipeline: Cắt tự động, chuyển văn bản, trích xuất Vector. |
| **Tuần 6-8** | Cài đặt kiến trúc SASRec, sinh dữ liệu giả lập và huấn luyện mô hình. |
| **Tuần 9-10**| Xây dựng Backend API (FastAPI) và tích hợp tìm kiếm Vector (IR). |
| **Tuần 11-12**| Xây dựng UI (giao diện vuốt dọc), kiểm thử toàn bộ và viết Báo cáo. |

---

## 8. Kết quả dự kiến (Expected Deliverables)
1. **Mã nguồn (Source Code):** Repo chứa toàn bộ hệ thống (AI Pipeline + Backend + UI).
2. **Báo cáo mô hình:** Các biểu đồ đánh giá (NDCG, Recall@K cho RecSys; WER cho Whisper).
3. **Sản phẩm Demo:** Video hoặc App mô phỏng giao diện vuốt với khả năng thay đổi gợi ý theo thời gian thực.

---

## 9. Cấu trúc Cơ sở dữ liệu (Database Schema Dự kiến)

*Sử dụng NoSQL (MongoDB) cho tính linh hoạt.*

### 9.1. Collection: `podcasts_full` (Tập gốc)
```json
{
  "_id": "pod_001",
  "title": "Tập 101: Cách vượt qua trì hoãn",
  "host": "Vietcetera",
  "duration": 3600,
  "source_url": "[youtube.com/](https://youtube.com/)..."
}