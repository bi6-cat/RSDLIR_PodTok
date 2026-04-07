import os
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import csv
import uuid
import time
import random

# Danh sách User-Agents giả mạo để chống chặn
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
]

# Cấu hình thư mục
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
CONFIG_DIR = os.path.join(DATA_DIR, "config")
CSV_FILE = os.path.join(DATA_DIR, "2_apple_podcast_links.csv")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CONFIG_DIR, exist_ok=True)

def search_apple_podcasts(keyword, limit=3):
    print(f"🔍 Đang tìm podcast về: '{keyword}'...")
    safe_keyword = urllib.parse.quote(keyword)
    url = f"https://itunes.apple.com/search?term={safe_keyword}&media=podcast&limit={limit}"
    
    # Chọn random User-Agent
    headers = {'User-Agent': random.choice(USER_AGENTS)}
    req = urllib.request.Request(url, headers=headers)
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
        print(f"❌ Lỗi: {e}")
        return []

def build_csv_sheet(keywords, max_channels=3, max_episodes=5):
    """
    Quét RSS và đẩy tất cả thông tin/Links tìm được vào 1 file CSV.
    KHÔNG download audio ở bước này.
    """
    print(f"📝 Bắt đầu thu thập Links và tạo Sheet tại: {CSV_FILE}")
    
    # Mở file CSV để ghi
    with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Ghi Header
        writer.writerow(['ID', 'Keyword', 'Podcast Name', 'Episode Title', 'Audio URL'])
        
        for keyword in keywords:
            discovered_feeds = search_apple_podcasts(keyword, limit=max_channels)
            
            for feed_info in discovered_feeds:
                feed_url = feed_info['feedUrl']
                podcast_name = feed_info['collectionName']
                
                try:
                    headers = {'User-Agent': random.choice(USER_AGENTS)}
                    req = urllib.request.Request(feed_url, headers=headers)
                    with urllib.request.urlopen(req) as response:
                        xml_data = response.read()
                        
                    root = ET.fromstring(xml_data)
                    channel = root.find('channel')
                    
                    items = channel.findall('item')[:max_episodes]
                    for item in items:
                        title = item.find('title').text
                        enclosure = item.find('enclosure')
                        
                        if enclosure is None:
                            continue
                            
                        mp3_url = enclosure.get('url')
                        unique_id = f"apple_{str(uuid.uuid4())[:8]}"
                        
                        # Ghi từng dòng vào CSV
                        writer.writerow([unique_id, keyword, podcast_name, title, mp3_url])
                        print(f"   ➕ Đã thêm vào Sheet: {title[:50]}...")
                        
                    # Chống chặn IP (Anti-ban) sau khi scrape mỗi RSS Feed
                    # Nghỉ ngẫu nhiên 1 - 2 giây (đã giảm)
                    sleep_time = random.uniform(1.0, 2.0)
                    print(f"   ⏳ Nghỉ {sleep_time:.1f}s để tránh bị block IP...")
                    time.sleep(sleep_time)
                        
                except Exception as e:
                    print(f"   ❌ Lỗi đọc feed {podcast_name}: {e}")

    print(f"\n🎉 HOÀN TẤT! Hãy mở file `data/2_apple_podcast_links.csv` bằng Excel hoặc VS Code.")
    print("👉 Xóa những dòng bạn KHÔNG CHỌN, lưu lại, sau đó chạy script tải Audio!")

if __name__ == "__main__":
    # Đọc từ khóa từ file
    KEYWORDS_FILE = os.path.join(CONFIG_DIR, "2_3_apple_keywords.txt")
    if not os.path.exists(KEYWORDS_FILE):
        with open(KEYWORDS_FILE, 'w', encoding='utf-8') as f:
            pass # Chỉ tạo file trống
        print(f"Đã tạo file trống tại {KEYWORDS_FILE}. Vui lòng thêm từ khóa vào file này rồi chạy lại.")
        
    with open(KEYWORDS_FILE, 'r', encoding='utf-8') as f:
        KWS = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    if not KWS:
        print(f"File {KEYWORDS_FILE} trống. Vui lòng thêm từ khóa.")
    else:
        # max_channels: Số kênh lấy cho mỗi chủ đề
        # max_episodes: Số tập lấy cho mỗi kênh
        build_csv_sheet(KWS, max_channels=2, max_episodes=3)