import os
import glob
import subprocess
import math

# Cấu hình thư mục
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
AUDIO_DIR = os.path.join(DATA_DIR, "raw_audio")

# Cấu hình cắt file DEMO
DEMO_DURATION_SECONDS = 600  # Lấy 10 phút đầu tiên (600 giây) của mỗi bài để đảm bảo nhận diện đúng chủ đề

def get_audio_duration(file_path: str) -> float:
    """Sử dụng ffprobe để lấy độ dài file audio (đơn vị: giây)."""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries",
             "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        return float(result.stdout.strip())
    except Exception as e:
        print(f"❌ Lỗi khi đọc độ dài file {file_path}: {e}")
        return 0.0

def split_audio_file(file_path: str, duration: int, start_time: int = 0):
    """Sử dụng ffmpeg để lấy một đoạn "Core Segment" của file audio cho mục đích demo."""
    dir_name = os.path.dirname(file_path)
    base_name, ext = os.path.splitext(os.path.basename(file_path))
    
    # Tạo thư mục output có dạng "tên_thư_mục_gốc" + "_split" (vd: raw_audio_1_split)
    # Nó sẽ được tạo trực tiếp bên trong data/
    parent_dir = os.path.dirname(dir_name)
    current_folder_name = os.path.basename(dir_name)
    output_dir = os.path.join(parent_dir, f"{current_folder_name}_split")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    # Định dạng tên file đầu ra đưa vào trong thư mục _split: tenfile_split.mp3
    output_path = os.path.join(output_dir, f"{base_name}_split{ext}")
    
    print(f"✂️  Đang cắt lấy {duration} giây bản split (từ giây {start_time}) file: {base_name}{ext}...")
    
    try:
        # Lệnh cắt ffmpeg siêu tốc (copy codec không re-encode), lấy chính xác 10 phút Phần Lõi
        subprocess.run(
            ["ffmpeg", "-y", "-ss", str(start_time), "-i", file_path, "-t", str(duration), "-c", "copy", output_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        
        # Tạm thời khóa tính năng xóa file gốc để bạn có thể test lại nhiều lần nếu muốn
        # Mở comment dòng dưới đây nếu bạn muốn thực sự xóa file gốc để tiết kiệm ổ cứng
        # os.remove(file_path)
        print(f"   ✅ Đã cắt xong bản demo và LƯU LẠI file gốc (chưa xóa)!")
        
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Lỗi khi cắt file {file_path}. FFmpeg error.")

if __name__ == "__main__":
    print(f"🔍 Đang quét toàn bộ thư mục data để tìm các thư mục chứa raw audio...")
    
    if not os.path.exists(DATA_DIR):
        print(f"Thư mục {DATA_DIR} không tồn tại!")
        exit()

    # Quét cả .mp3 và .m4a trong tất cả các thư mục con (raw_audio, raw_audio_1, raw_audio_2, ...)
    audio_files = []
    for ext in ("*.mp3", "*.m4a"):
        for f in glob.glob(os.path.join(DATA_DIR, "raw_audio*", "**", ext), recursive=True):
            # Không quét vào các thư mục đã được cắt (chứa _split)
            if "_split" not in str(f):
                audio_files.append(f)
        
    if not audio_files:
        print("Không tìm thấy file audio nào trong các thư mục raw_audio* (chưa cắt).")
        exit()

    processed_count = 0

    for file_path in audio_files:
        duration = get_audio_duration(file_path)
        
        # Bỏ qua các file rác quá ngắn < 2 phút (120s)
        if duration >= 120:
            # Thuật toán đi tìm "Phần Lõi" (Core Segment) của Podcast tránh Intro/Quảng cáo
            if duration <= DEMO_DURATION_SECONDS:
                start_time = 0
            else:
                # Bỏ qua 1/3 thời lượng đầu tiên, nhưng tối đa nhảy cóc 15 phút (900 giây)
                skip_time = min(900, int(duration / 3))
                start_time = skip_time
                
            split_audio_file(file_path, duration=DEMO_DURATION_SECONDS, start_time=start_time)
            processed_count += 1
            
    print(f"\n🎉 HOÀN TẤT! Đã xử lý lấy mẫu demo {processed_count} file âm thanh.")
