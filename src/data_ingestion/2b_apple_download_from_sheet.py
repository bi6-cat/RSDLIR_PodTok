import os
import csv
import json
import urllib.request
import time
import argparse

# Cấu hình thư mục
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
AUDIO_DIR = os.path.join(DATA_DIR, "raw_audio", "2_apple_sheet")
METADATA_FILE = os.path.join(DATA_DIR, "2_apple_sheet_metadata.json")

os.makedirs(AUDIO_DIR, exist_ok=True)

def download_audio_from_csv(csv_filename="2_apple_podcast_links.csv"):
    """
    Đọc file CSV (chứa các links bạn ĐÃ CHỌN).
    Tiến hành tải file mp3 xuống máy.
    """
    csv_file_path = os.path.join(DATA_DIR, csv_filename)
    if not os.path.exists(csv_file_path):
        print(f"❌ KHÔNG TÌM THẤY {csv_file_path}!")
        print("Hãy chạy lệnh `1_build_link_sheet.py` (hoặc check lại file đã chia nhỏ) trước.")
        return

    metadata_list = []
    
    # Đọc Metadata cũ nếu có (để append thêm)
    if os.path.exists(METADATA_FILE):
        try:
            with open(METADATA_FILE, 'r', encoding='utf-8') as f:
                metadata_list = json.load(f)
        except json.JSONDecodeError:
            pass

    print(f"🚀 BẮT ĐẦU TẢI MP3 TỪ SHEET: {csv_file_path}")
    
    # Đếm số dòng để lấy số lượng
    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        
    print(f"📦 Đã tìm thấy {len(rows)} bài cần tải.")
    
    for row in rows:
        unique_id = row['ID']
        keyword = row['Keyword']
        podcast_name = row['Podcast Name']
        title = row['Episode Title']
        mp3_url = row['Audio URL']
        
        file_name = f"{unique_id}.mp3"
        file_path = os.path.join(AUDIO_DIR, file_name)
        
        # Nếu đã tải rồi thì bỏ qua
        if os.path.exists(file_path):
            print(f"⏩ Đã tải rồi: {title[:40]}... (Bỏ qua)")
            continue
            
        print(f"⬇️ Đang tải tập: {title[:50]}...")
        
        try:
            # Tạo luồng Request chuẩn giả mạo trình duyệt để không bị cấm tải
            req = urllib.request.Request(
                mp3_url, 
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
                }
            )
            with urllib.request.urlopen(req) as response:
                # Đọc dữ liệu stream và lưu dần vào file thay vì nạp RAM (urlretrieve không nạp RAM được)
                with open(file_path, 'wb') as out_file:
                    out_file.write(response.read())
            
            # Cập nhật thông tin JSON để chạy AI bài sau
            meta = {
                "_id": unique_id,
                "title": title,
                "host": podcast_name,
                "keyword": keyword,
                "source_url": mp3_url,
                "audio_file": file_name
            }
            metadata_list.append(meta)
            
            # Ghi ngay lập tức sau mỗi bài tải xong
            with open(METADATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(metadata_list, f, ensure_ascii=False, indent=4)
                
            print(f"   ✅ [THÀNH CÔNG] Đã lưu file: {file_name}")
            
            # Anti-ban (Chống bị khóa IP): Ngủ một khoảng thời gian ngẫu nhiên 1-2 giây (đã giảm)
            import random
            sleep_time = random.uniform(1.0, 2.0)
            time.sleep(sleep_time) 
            
        except Exception as e:
            print(f"   ❌ Lỗi tải file: {mp3_url[:40]}... Error: {str(e)}")
            
    print("\n🎉 HOÀN TẤT TẢI DỮ LIỆU! Tất cả audio đã có trong thư mục `raw_audio_mass`.")
    print("Bây giờ bạn có thể gọi AI Whisper chạy mốc thời gian!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Tải audio từ file CSV.')
    parser.add_argument('--csv', type=str, default='2_apple_podcast_links.csv', 
                        help='Tên file chứa links CSV (ví dụ: 2_apple_podcast_links_part01.csv)')
    args = parser.parse_args()
    
    download_audio_from_csv(csv_filename=args.csv)