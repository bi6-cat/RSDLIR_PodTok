# current-status

File này tóm tắt nhanh tình hình hiện tại của data pipeline, quá trình train baseline, và gói dữ liệu `ready-data`.

## 1. Mục tiêu đã thực hiện đến hiện tại

Dự án đã trải qua 3 bước chính:

1. Tạo data item từ podcast gốc.
2. Train SASRec baseline để kiểm tra end-to-end.
3. Đóng gói package `ready-data` để dùng chung cho train và web demo.

## 2. Đã làm gì với dữ liệu

### 2.1 Tạo best segment audio

- Đầu vào ban đầu là audio podcast đầy đủ + transcript + metadata.
- Đã chạy pipeline để cắt ra các đoạn ngắn khoảng 30-45 giây.
- Mỗi episode giữ lại 1 best segment final.
- Đã QA và loại trùng trước khi xuất file final.

Kết quả final:

- `105` item cuối
- `105` best segment audio
- File source-of-truth: `catalog/item_metadata_final.jsonl`

### 2.2 Tạo dữ liệu tương tác mock cho train/demo

- Đã tạo các profile user và interaction logs mock.
- Mục đích để có dữ liệu tuần tự cho SASRec và có data giả lập cho web demo.

Kết quả hiện tại:

- `125816` sự kiện tương tác
- `8` demo user

File chính:

- `interactions/mock/user_interactions.jsonl`
- `demo/users/demo_users.json`
- `demo/users/demo_user_history.json`

### 2.3 Mapping audio đầy đủ (full audio)

- Đã mapping audio đầy đủ cho tất cả item final.
- Có 1 trường hợp alias:
- `apple_37642eda <- apple_af20a0ea.mp3`

Kết quả hiện tại:

- `105/105` item cuối đã có `full_audio_path`
- Metadata nguồn của audio đầy đủ nằm trong `catalog/full_audio_source_metadata.json`
- Mapping episode -> full audio nằm trong `catalog/episode_audio_map.jsonl`

## 3. Đã train baseline

Đã train SASRec baseline để test pipeline train/eval.

Các chỉ số hiện tại:

- valid `hit@10 = 0.489`
- valid `ndcg@10 = 0.404`
- test `hit@10 = 0.441`
- test `ndcg@10 = 0.3626`

Các file liên quan:

- `training/sasrec/train_sequences.jsonl` (`32802` dòng)
- `training/sasrec/valid_sequences.jsonl` (`1000` dòng)
- `training/sasrec/test_sequences.jsonl` (`1000` dòng)
- `training/sasrec/valid_metrics.json`
- `training/sasrec/test_metrics.json`
- `training/sasrec/train_history.json`
- `training/sasrec/model_state.pt`
- `reports/training_summary.json`

## 4. `ready-data` hiện tại có gì

### Catalog

- `catalog/item_metadata_final.jsonl`: item cuối dùng cho train/demo
- `catalog/item_id_map.json`: map `clip_id -> item_id`
- `catalog/episode_audio_map.jsonl`: map `episode_id -> full_audio_path`
- `catalog/full_audio_source_metadata.json`: metadata gốc của audio đầy đủ

### Audio assets

- `assets/best_segment_audios/`: audio ngắn dùng cho feed/demo
- `assets/full_audios/`: audio đầy đủ để replay / detail / trace nguồn

### Interactions

- `interactions/mock/`: dữ liệu tương tác mock để train và demo

### Training

- `training/sasrec/`: file sequence, metrics, history, checkpoint baseline

### Demo

- `demo/ui/demo_config.json`: file bắt đầu cho web demo
- `demo/feed/`: feed items và featured items
- `demo/users/`: demo user và lịch sử
- `demo/recommendations/`: mock recommendations

### Reports

- `reports/training_summary.json`
- `reports/full_audio_match_summary.json`
- `reports/full_audio_download_report.json`

## 5. Nên dùng package này như thế nào

### Nếu làm web demo

- Bắt đầu từ `demo/ui/demo_config.json`
- Render feed bằng `demo/feed/feed_items.json`
- Join audio bằng `clip_audio_path`
- Nếu cần audio đầy đủ thì join bằng `full_audio_path`
- Không suy ra item list bằng cách scan thư mục audio

### Nếu tiếp tục train model

- Bắt đầu từ `catalog/item_metadata_final.jsonl`
- Dùng `item_id_map.json` cho id dạng số nguyên
- Dùng `interactions/mock/user_interactions.jsonl` hoặc bộ sequence có sẵn trong `training/sasrec/`

## 6. Tình trạng hiện tại

Package `ready-data` đã ở trạng thái rất gần final:

- Đã có data item final
- Đã có dữ liệu tương tác mock
- Đã có train baseline
- Đã đủ audio best segment
- Đã đủ audio đầy đủ
- Đã có tài liệu cơ bản

## 7. Việc hợp lý tiếp theo

1. Publish `ready-data` thành dataset final.
2. Bàn giao file này + `ready-data/README.md` cho Quang.
3. Sau đó quay lại tối ưu model / retrieval / vector search.
