import os
import json
import urllib.request
import xml.etree.ElementTree as ET

# Cấu hình thư mục
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
AUDIO_DIR = os.path.join(DATA_DIR, "raw_audio", "4_direct_rss")
METADATA_FILE = os.path.join(DATA_DIR, "4_direct_rss_metadata.json")

os.makedirs(AUDIO_DIR, exist_ok=True)

def fetch_sample_from_rss(rss_url, limit=1):
    """
    Lấy file trực tiếp từ nguồn RSS Podcast chuẩn.
    Nhanh, sạch, không cần dùng tool crawl phức tạp.
    """
    print(f"📡 Đang đọc RSS từ: {rss_url}")
    req = urllib.request.Request(rss_url, headers={'User-Agent': 'Mozilla/5.0'})
    
    try:
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
            
        root = ET.fromstring(xml_data)
        channel = root.find('channel')
        podcast_title = channel.find('title').text
        
        print(f"✅ Đã kết nối kênh: {podcast_title}")
        
        metadata_list = []
        items = channel.findall('item')[:limit]
        
        for i, item in enumerate(items):
            title = item.find('title').text
            # Tìm link file MP3 trong thẻ enclosure
            enclosure = item.find('enclosure')
            if enclosure is None:
                continue
                
            mp3_url = enclosure.get('url')
            video_id = f"rss_sample_{i+1}"
            file_name = f"{video_id}.mp3"
            file_path = os.path.join(AUDIO_DIR, file_name)
            
            print(f"\n⬇️ Đang tải tập: {title}")
            print(f"🔗 Link: {mp3_url[:60]}...")
            
            # Tải file MP3 về
            urllib.request.urlretrieve(mp3_url, file_path)
            
            # Tạo Metadata
            meta = {
                "_id": video_id,
                "title": title,
                "host": podcast_title,
                "source_url": mp3_url,
                "audio_file": file_name
            }
            metadata_list.append(meta)
            print(f"✅ Đã lưu file: {file_path}")
            
        # Ghi metadata
        with open(METADATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(metadata_list, f, ensure_ascii=False, indent=4)
            
        print(f"\n🎉 XONG! Đã có 1 file mp3 sạch sẽ để bạn test vào flow AI cắt/chữ.")
        
    except Exception as e:
        print(f"❌ Lỗi: {str(e)}")

if __name__ == "__main__":
    # Đọc link RSS từ file
    RSS_FILE = os.path.join(DATA_DIR, "4_rss_links.txt")
    if not os.path.exists(RSS_FILE):
        with open(RSS_FILE, 'w', encoding='utf-8') as f:
            pass # Chỉ tạo file trống
        print(f"Đã tạo file trống tại {RSS_FILE}. Vui lòng thêm link RSS XML vào file này rồi chạy lại.")
        
    with open(RSS_FILE, 'r', encoding='utf-8') as f:
        rss_links = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    if not rss_links:
        print(f"File {RSS_FILE} trống. Vui lòng thêm link RSS.")
    else:
        for rss in rss_links:
            fetch_sample_from_rss(rss, limit=1)
