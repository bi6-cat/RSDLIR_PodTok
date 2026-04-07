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
        'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
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
        'sleep_requests': 2.5, # Chống chặn IP (rate limit) từ Youtube
        'max_sleep_interval': 15, # Khoảng thời gian ngủ tối đa
        'sleep_interval': 5, # Giãn cách random giữa các file từ 5 -> 15 giây
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
                # Trích xuất thông tin trước
                info_dict = ydl.extract_info(url, download=False)
                if not info_dict:
                    continue
                
                video_id = info_dict.get('id')
                if video_id in downloaded_ids:
                    print(f"Bỏ qua (đã tải): {video_id} - {info_dict.get('title')}")
                    continue
                
                # Tiến hành download thực tế
                ydl.download([url])
                
                # Lưu Metadata
                meta = {
                    "_id": video_id,
                    "title": info_dict.get('title'),
                    "host": info_dict.get('uploader'),
                    "duration": info_dict.get('duration'), # seconds
                    "source_url": url,
                    "view_count": info_dict.get('view_count'),
                    "upload_date": info_dict.get('upload_date'),
                    "audio_file": f"{video_id}.mp3"
                }
                metadata_list.append(meta)
                print(f"Đã lưu thành công: {meta['title']}")
                
            except Exception as e:
                print(f"Lỗi khi tải {url}: {str(e)}")
                
    # Lưu lại file JSON
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata_list, f, ensure_ascii=False, indent=4)
        
    print(f"\nĐã hoàn thành! Metadata được lưu tại: {METADATA_FILE}")
    return metadata_list

if __name__ == "__main__":
    # Đọc link từ file
    URLS_FILE = os.path.join(DATA_DIR, "1_youtube_urls.txt")
    if not os.path.exists(URLS_FILE):
        with open(URLS_FILE, 'w', encoding='utf-8') as f:
            f.write("https://www.youtube.com/playlist?list=PLLoEwO2Vv1F28vB7sPzexA0YttN1G7Ld9\n")
            f.write("https://www.youtube.com/playlist?list=PL_If5XqH_t41-Yv9jDIn90uN7I-pM3K5n\n")
            f.write("https://www.youtube.com/@Web5Ngay/videos\n")
        print(f"Đã tạo file mẫu tại {URLS_FILE}. Vui lòng cập nhật link trong file này.")
        
    with open(URLS_FILE, 'r', encoding='utf-8') as f:
        sample_urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    if not sample_urls:
        print(f"File {URLS_FILE} trống. Vui lòng thêm link.")
    else:
        print("🚀 BẮT ĐẦU CRAWL PLAYLIST PODCAST DỮ LIỆU PHASE 1...")
        download_podcasts(sample_urls)
