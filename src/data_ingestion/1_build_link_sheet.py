import os
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import csv
import uuid

# Cấu hình thư mục
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
CSV_FILE = os.path.join(DATA_DIR, "podcast_links_sheet.csv")

os.makedirs(DATA_DIR, exist_ok=True)

def search_apple_podcasts(keyword, limit=3):
    print(f"🔍 Đang tìm podcast về: '{keyword}'...")
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
                    req = urllib.request.Request(feed_url, headers={'User-Agent': 'Mozilla/5.0'})
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
                        unique_id = f"pod_{str(uuid.uuid4())[:8]}"
                        
                        # Ghi từng dòng vào CSV
                        writer.writerow([unique_id, keyword, podcast_name, title, mp3_url])
                        print(f"   ➕ Đã thêm vào Sheet: {title[:50]}...")
                        
                except Exception as e:
                    print(f"   ❌ Lỗi đọc feed {podcast_name}: {e}")

    print(f"\n🎉 HOÀN TẤT! Hãy mở file `data/podcast_links_sheet.csv` bằng Excel hoặc VS Code.")
    print("👉 Xóa những dòng bạn KHÔNG CHỌN, lưu lại, sau đó chạy script tải Audio!")

if __name__ == "__main__":
    # Điền chủ đề bạn muốn cào link
    KWS = ["tâm lý học", "phát triển bản thân", "giáo dục", "tài chính"]
    
    # max_channels: Số kênh lấy cho mỗi chủ đề
    # max_episodes: Số tập lấy cho mỗi kênh
    build_csv_sheet(KWS, max_channels=2, max_episodes=3)