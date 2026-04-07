import os
import json
import yt_dlp
from typing import List, Dict

# Cấu hình thư mục lưu trữ
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
AUDIO_DIR = os.path.join(DATA_DIR, "raw_audio", "1_youtube")
METADATA_FILE = os.path.join(DATA_DIR, "1_youtube_metadata.json")

# Đảm bảo thư mục tồn tại
os.makedirs(AUDIO_DIR, exist_ok=True)

def get_ytdlp_opts(output_dir: str) -> dict:
    """
    Cấu hình yt-dlp:
    - Chỉ tải audio
    - Format m4a hoặc mp3
    - Sample rate 16kHz (rất quan trọng cho mô hình Whisper và Wav2Vec)
    """
    return {
        'format': 'bestaudio[ext=m4a]/bestaudio/best', # Ưu tiên định dạng m4a siêu nhẹ thay vì webm
        'outtmpl': os.path.join(output_dir, 'yt_%(id)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '64', # Ép chất lượng 64kbps để file cực kỳ nhẹ, AI Whisper vẫn nghe cực rõ do là file giọng nói
        }],
        'postprocessor_args': [
            '-ar', '16000',
            '-ac', '1'
        ],
        'playlist_items': '1-5', # CHỈ TẢI 5 TẬP MỚI NHẤT TRONG PLAYLIST
        'sleep_requests': 1.0, # Chống chặn IP (rate limit) từ Youtube - Đã giảm
        'max_sleep_interval': 5, # Khoảng thời gian ngủ tối đa - Đã giảm
        'sleep_interval': 2, # Giãn cách random giữa các file từ 2 -> 5 giây
        'extract_flat': False,
        'quiet': False,
        'no_warnings': True,
        'ignoreerrors': True
    }

def download_podcasts(urls: List[str]) -> List[Dict]:
    """Tải âm thanh và trích xuất metadata từ danh sách YouTube URL."""
    metadata_list = []
    
    # Load metadata hiện tại nếu đã có để không tải lại
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            metadata_list = json.load(f)
    
    downloaded_ids = {item['_id'] for item in metadata_list}
    
    opts = get_ytdlp_opts(AUDIO_DIR)
    
    with yt_dlp.YoutubeDL(opts) as ydl:
        for url in urls:
            try:
                print(f"\nĐang xử lý URL: {url}")
                # Trích xuất thông tin VÀ tự động tải
                info_dict = ydl.extract_info(url, download=True)
                if not info_dict:
                    continue
                
                # Kiểm tra xem đây là playlist hay video đơn
                videos_to_process = []
                if 'entries' in info_dict:
                    # Là Playlist hoặc Kênh: Lấy danh sách các video bên trong
                    videos_to_process = [entry for entry in info_dict['entries'] if entry is not None]
                else:
                    # Là Video đơn
                    videos_to_process = [info_dict]
                    
                for video_info in videos_to_process:
                    raw_id = video_info.get('id')
                    video_id = f"yt_{raw_id}"
                    
                    if video_id in downloaded_ids:
                        print(f"Bỏ qua ghi metadata (đã có): {video_id}")
                        continue
                    
                    # Lưu Metadata cho từng video (từng tập podcast)
                    meta = {
                        "_id": video_id,
                        "title": video_info.get('title'),
                        "host": video_info.get('uploader') or info_dict.get('uploader'),
                        "duration": video_info.get('duration'), # seconds
                        "source_url": video_info.get('webpage_url') or f"https://www.youtube.com/watch?v={raw_id}",
                        "view_count": video_info.get('view_count'),
                        "upload_date": video_info.get('upload_date'),
                        "audio_file": f"{video_id}.mp3"
                    }
                    metadata_list.append(meta)
                    downloaded_ids.add(video_id)
                    print(f"✅ Đã lưu metadata: {meta['title']}")
                
            except Exception as e:
                print(f"❌ Lỗi khi tải {url}: {str(e)}")
                
    # Lưu lại file JSON sau mỗi lượt tải playlist
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata_list, f, ensure_ascii=False, indent=4)
        
    print(f"\nĐã hoàn thành! Metadata được lưu tại: {METADATA_FILE}")
    return metadata_list

if __name__ == "__main__":
    # Đọc link từ file
    URLS_FILE = os.path.join(DATA_DIR, "1_youtube_urls.txt")
    if not os.path.exists(URLS_FILE):
        with open(URLS_FILE, 'w', encoding='utf-8') as f:
            pass # Chỉ tạo file trống
        print(f"Đã tạo file trống tại {URLS_FILE}. Vui lòng thêm link YouTube vào file này rồi chạy lại.")
        
    with open(URLS_FILE, 'r', encoding='utf-8') as f:
        sample_urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    if not sample_urls:
        print(f"File {URLS_FILE} trống. Vui lòng thêm link.")
    else:
        print("🚀 BẮT ĐẦU CRAWL PLAYLIST PODCAST DỮ LIỆU PHASE 1...")
        download_podcasts(sample_urls)
