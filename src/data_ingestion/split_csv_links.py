import os
import csv
import math

# Cấu hình thư mục
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
CSV_FILE = os.path.join(DATA_DIR, "2_apple_podcast_links.csv")

def split_csv_into_chunks(num_chunks=10):
    """
    Đọc file CSV tổng và chia nhỏ thành N file nhỏ hơn.
    Rất hữu ích khi bạn muốn chạy song song trên nhiều máy/tài khoản Colab,
    hoặc sợ rớt mạng giữa chừng khi tải số lượng lớn.
    """
    if not os.path.exists(CSV_FILE):
        print(f"❌ Không tìm thấy file {CSV_FILE}!")
        print("Hãy chạy script `2a_apple_build_link_sheet.py` trước để tạo dữ liệu.")
        return

    # Đọc dữ liệu
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            print("❌ File CSV trống!")
            return
            
        rows = list(reader)

    total_rows = len(rows)
    if total_rows == 0:
        print("❌ Không có dòng dữ liệu nào trong CSV để chia nhỏ!")
        return

    # Tính toán số lượng mỗi file
    chunk_size = math.ceil(total_rows / num_chunks)
    print(f"📦 Đã tìm thấy: {total_rows} âm thanh cần tải.")
    print(f"🔪 Đang chia xẻ nhỏ thành {num_chunks} file (Khoảng {chunk_size} file mp3 / 1 CSV)...\n")

    for i in range(num_chunks):
        start_idx = i * chunk_size
        end_idx = min(start_idx + chunk_size, total_rows)
        chunk_rows = rows[start_idx:end_idx]

        if not chunk_rows:
            continue # Nếu khúc cuối không còn dữ liệu thì bỏ qua

        # Tạo tên file mới
        part_filename = f"2_apple_podcast_links_part{i+1:02d}.csv"
        part_filepath = os.path.join(DATA_DIR, part_filename)
        
        with open(part_filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(chunk_rows)

        print(f"   ✅ Đã tạo: {part_filename} (Chứa {len(chunk_rows)} âm thanh)")
        
    print(f"\n🎉 HOÀN TẤT! Các file CSV nhỏ đã được bung ra tại `data/`.")
    print("👉 Mẹo: Bạn có thể đưa các file part này lên từng máy Colab riêng, rồi cấu hình `2b_apple_download_from_sheet.py` trỏ vào tên file tương ứng để TẢI SONG SONG x10 tốc độ!")

if __name__ == "__main__":
    # Thay đổi số 10 thành số file bạn muốn chia
    split_csv_into_chunks(10)
