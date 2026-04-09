import os
import glob
import subprocess
import math

# Cấu hình thư mục
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
AUDIO_DIR = os.path.join(DATA_DIR, "raw_audio")

# Cấu hình cắt file (Tránh dài quá để tối ưu Model ASR)
MAX_CHUNK_DURATION = 600  # Lấy một đoạn dài 10 phút (600 giây) để Model Text có đủ ngữ cảnh tìm điểm "Peak"
NUM_CLIPS_PER_AUDIO = 1

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

def split_audio_file(file_path: str, duration: int, start_time: int, clip_index: int):
    """Sử dụng ffmpeg để lấy một đoạn "vàng" (Core Segment) của file audio."""
    dir_name = os.path.dirname(file_path)
    base_name, ext = os.path.splitext(os.path.basename(file_path))
    
    # Tạo thư mục output có dạng "tên_thư_mục_gốc" + "_split" (vd: raw_audio_split)
    parent_dir = os.path.dirname(dir_name)
    current_folder_name = os.path.basename(dir_name)
    output_dir = os.path.join(parent_dir, f"{current_folder_name}_split")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    # Định dạng tên file đầu ra: chude_1234_clip_1.mp3
    output_path = os.path.join(output_dir, f"{base_name}_clip_{clip_index}{ext}")
    
    # Nếu file đã được cắt rồi thì bỏ qua không cắt lại nữa
    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        print(f"⏩ Đã cắt rồi: {base_name}_clip_{clip_index}{ext} (Bỏ qua)")
        return

    print(f"✂️  Đang cắt lấy {duration}s bảng clip {clip_index} (từ phút {start_time//60}) file: {base_name}{ext}...")
    
    try:
        # Lệnh cắt ffmpeg siêu tốc (copy codec không re-encode), lấy chuẩn thời điểm
        subprocess.run(
            ["ffmpeg", "-y", "-ss", str(start_time), "-i", file_path, "-t", str(duration), "-c", "copy", output_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        
        # Kiểm tra file output có bị 0KB (lỗi ffmpeg xuất file rỗng)
        if os.path.exists(output_path) and os.path.getsize(output_path) == 0:
            print(f"   ❌ Lỗi cắt: File {base_name}_clip_{clip_index}{ext} sinh ra bị 0KB. Đã xóa!")
            os.remove(output_path)
        else:
            print(f"   ✅ Đã cắt clip {clip_index} thành công!")
            
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Lỗi khi cắt file {file_path}. FFmpeg error.")
        if os.path.exists(output_path):
            os.remove(output_path)

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
        file_size_kb = os.path.getsize(file_path) / 1024
        
        # Tiêu chuẩn chất lượng: Audio gốc phải dài ít nhất 7 phút (420s) và lớn hơn 4MB
        if duration >= 420 and file_size_kb >= 4000:
            # Bỏ qua 10% đoạn đầu tiên hoặc tối đa 3 phút (tránh intro, lặp lời chào)
            # Lấy 1 đoạn dài (ví dụ: 15 phút) để có đủ text cho mô hình NLP đọc "Peak"
            start_point = min(180, int(duration * 0.10))
            
            # Đảm bảo phần cắt không vượt quá tổng thời lượng audio
            chunk_length = min(MAX_CHUNK_DURATION, int(duration - start_point))
            
            if chunk_length > 60: # Ít nhất đoạn này phải dài hơn 1 phút mới đáng xử lý
                split_audio_file(file_path, duration=chunk_length, start_time=start_point, clip_index=1)
                processed_count += 1
            
    print(f"\n🎉 HOÀN TẤT! Đã tiền xử lý {processed_count} tệp (bỏ qua intro và giới hạn độ dài).")
