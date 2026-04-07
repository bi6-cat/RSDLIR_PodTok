import os
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import time

# Cấu hình thư mục
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
CONFIG_DIR = os.path.join(DATA_DIR, "config")
AUDIO_DIR = os.path.join(DATA_DIR, "raw_audio", "3_apple_auto_discover")
METADATA_FILE = os.path.join(DATA_DIR, "3_apple_auto_metadata.json")

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(CONFIG_DIR, exist_ok=True)

def search_apple_podcasts(keyword, limit=5):
    """
    Sử dụng API miễn phí của Apple (iTunes) để tìm kiếm các kênh Podcast.
    Trả về danh sách các RSS Link URL của các kênh Podcast đó.
    """
    print(f"\n🔍 Đang tìm kiếm Podcast với từ khóa: '{keyword}' trên Apple Podcasts...")
    
    # Bỏ khoảng trắng và mã hóa từ khóa
    safe_keyword = urllib.parse.quote(keyword)
    url = f"https://itunes.apple.com/search?term={safe_keyword}&media=podcast&limit={limit}"
    
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            
        rss_urls = []
        for result in data.get('results', []):
            if 'feedUrl' in result:
                rss_urls.append({
                    'collectionName': result.get('collectionName', 'Unknown'),
                    'feedUrl': result['feedUrl']
                })
        return rss_urls
    except Exception as e:
        print(f"❌ Lỗi tìm kiếm Apple API: {e}")
        return []

def fetch_episodes_from_rss(rss_list, max_episodes_per_feed=2):
    """
    Tải file MP3 từ danh sách RSS đã tìm được.
    """
    metadata_list = []
    
    # Load metadata hiện tại để lấy ID tăng dần
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            try:
                metadata_list = json.load(f)
            except:
                pass
                
    total_downloaded = len(metadata_list)

    for feed_info in rss_list:
        feed_url = feed_info['feedUrl']
        podcast_name = feed_info['collectionName']
        print(f"\n📡 Đang trích xuất kênh: {podcast_name}")
        
        try:
            req = urllib.request.Request(feed_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                xml_data = response.read()
                
            root = ET.fromstring(xml_data)
            channel = root.find('channel')
            
            items = channel.findall('item')[:max_episodes_per_feed]
            
            for item in items:
                title = item.find('title').text
                enclosure = item.find('enclosure')
                
                if enclosure is None:
                    continue
                    
                mp3_url = enclosure.get('url')
                
                total_downloaded += 1
                video_id = f"apple_auto_{total_downloaded:04d}"
                file_name = f"{video_id}.mp3"
                file_path = os.path.join(AUDIO_DIR, file_name)
                
                print(f"   ⬇️ Đang tải tập: {title[:50]}...")
                
                # Tải file Audio
                urllib.request.urlretrieve(mp3_url, file_path)
                
                # Cập nhật Metadata
                meta = {
                    "_id": video_id,
                    "title": title,
                    "host": podcast_name,
                    "source_url": mp3_url,
                    "audio_file": file_name,
                    "keyword_category": keyword
                }
                metadata_list.append(meta)
                
                # Lưu metadata liên tục để tránh mất dữ liệu nếu lỗi giữa chừng
                with open(METADATA_FILE, 'w', encoding='utf-8') as f:
                    json.dump(metadata_list, f, ensure_ascii=False, indent=4)
                    
                time.sleep(1) # Tránh bị chặn IP vì tải quá nhanh
                
        except Exception as e:
            print(f"   ❌ Lỗi khi đọc feed của {podcast_name}: {e}")

if __name__ == "__main__":
    # Đọc từ khóa từ file
    KEYWORDS_FILE = os.path.join(CONFIG_DIR, "2_3_apple_keywords.txt")
    if not os.path.exists(KEYWORDS_FILE):
        with open(KEYWORDS_FILE, 'w', encoding='utf-8') as f:
            pass # Chỉ tạo file trống
        print(f"Đã tạo file trống tại {KEYWORDS_FILE}. Vui lòng thêm từ khóa vào file này rồi chạy lại.")
        
    with open(KEYWORDS_FILE, 'r', encoding='utf-8') as f:
        keywords = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
    if not keywords:
        print(f"File {KEYWORDS_FILE} trống. Vui lòng thêm từ khóa.")
    else:
        for keyword in keywords:
            # 1. Tự động mượn API Apple để tìm 2 kênh hot nhất cho mỗi chủ đề
            discovered_feeds = search_apple_podcasts(keyword, limit=2)
            
            if discovered_feeds:
                # 2. Tự động quét RSS của các kênh đó và tải 2 tập mới nhất về
                fetch_episodes_from_rss(discovered_feeds, max_episodes_per_feed=2)
                
        print("\n🎉 HOÀN TẤT CHIẾN DỊCH CÀO DỮ LIỆU TỰ ĐỘNG TỪ APPLE PODCASTS!")
