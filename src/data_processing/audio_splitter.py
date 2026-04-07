import os
import glob
import subprocess
import math

# Cấu hình thư mục
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
AUDIO_DIR = os.path.join(DATA_DIR, "raw_audio")

# Cấu hình cắt file
MAX_DURATION_SECONDS = 1800  # 30 phút. Nếu file dài hơn 30 phút thì mới cắt.
CHUNK_SIZE_SECONDS = 900     # 15 phút. Mỗi phần cắt ra sẽ dài 15 phút (hoặc tùy chỉnh).

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

def split_audio_file(file_path: str, chunk_time: int):
    """Sử dụng ffmpeg để cắt file audio ra thành nhiều phần nhỏ (Lossless - Không làm giảm chất lượng)."""
    dir_name = os.path.dirname(file_path)
    base_name, ext = os.path.splitext(os.path.basename(file_path))
    
    # Định dạng tên file đầu ra: tenfile_part000.mp3, tenfile_part001.mp3...
    output_pattern = os.path.join(dir_name, f"{base_name}_part%03d{ext}")
    
    print(f"✂️  Đang cắt file: {base_name}{ext} (Mỗi phần {chunk_time//60} phút)...")
    
    try:
        # Lệnh cắt ffmpeg siêu tốc (copy codec không re-encode)
        subprocess.run(
            ["ffmpeg", "-i", file_path, "-f", "segment", "-segment_time", str(chunk_time), "-c", "copy", output_pattern],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        
        # Xóa file Gốc khổng lồ để tiết kiệm dung lượng (rất quan trọng trên Colab/Kaggle)
        os.remove(file_path)
        print(f"   ✅ Đã cắt xong và xóa file gốc để giải phóng bộ nhớ!")
        
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Lỗi khi cắt file {file_path}. FFmpeg error.")

if __name__ == "__main__":
    print(f"🔍 Đang quét toàn bộ thư mục: {AUDIO_DIR}")
    
    if not os.path.exists(AUDIO_DIR):
        print(f"Thư mục {AUDIO_DIR} không tồn tại!")
        exit()

    # Quét cả .mp3 và .m4a
    audio_files = []
    for ext in ("*.mp3", "*.m4a"):
        audio_files.extend(glob.glob(os.path.join(AUDIO_DIR, "**", ext), recursive=True))
        
    if not audio_files:
        print("Không tìm thấy file audio nào.")
        exit()

    processed_count = 0
    
    for file_path in audio_files:
        # Bỏ qua những file đã được cắt (chứa đuôi _part00) để không cắt lặp lại
        if "_part" in os.path.basename(file_path):
            continue
            
        duration = get_audio_duration(file_path)
        
        if duration > MAX_DURATION_SECONDS:
            mins = math.floor(duration / 60)
            print(f"\n⚠️ Phát hiện file siêu dài ({mins} phút): {os.path.basename(file_path)}")
            split_audio_file(file_path, chunk_time=CHUNK_SIZE_SECONDS)
            processed_count += 1
            
    print(f"\n🎉 HOÀN TẤT! Đã xử lý phân mảnh {processed_count} file âm thanh quá thời lượng.")
