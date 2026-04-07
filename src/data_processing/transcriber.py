import os
import json
from faster_whisper import WhisperModel
import warnings

# Tắt cảnh báo FP16 trên CPU (nếu không có GPU)
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

# Thiết lập đường dẫn thư mục
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
AUDIO_DIR = os.path.join(DATA_DIR, "raw_audio")
TRANSCRIPT_DIR = os.path.join(DATA_DIR, "transcripts")

os.makedirs(TRANSCRIPT_DIR, exist_ok=True)

def transcribe_audio(audio_path: str, model_size: str = "small"):
    """
    Sử dụng Faster-Whisper (tối ưu hóa C++) để tự động tạo phụ đề (Subtitles) 
    và lấy Timestamps từ file Audio. Tốc độ vắt kiệt sức mạnh RTX 5060.
    """
    print(f"\n[1] Đang tải mô hình AI Faster-Whisper (Size: {model_size})...")
    # Tối ưu hoá đặc biệt cho card RTX (device="cuda", compute_type="float16")
    # Nếu máy không có card màn hình, tự động rớt về CPU
    try:
        model = WhisperModel(model_size, device="cuda", compute_type="float16")
    except Exception:
        print("⚠️ CUDA báo lỗi hoặc không có, chuyển về chạy CPU tạm thời...")
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        
    file_name = os.path.basename(audio_path)
    print(f"[2] Bắt đầu nghe và tạo Subtitle cho: {file_name}")
    print("    Quá trình này sẽ sử dụng tối đa hiệu năng của Card... Bắt đầu ngay!")
    
    # Chạy AI Transcribe với beam_size, ép ngôn ngữ Tiếng Việt
    segments, info = model.transcribe(audio_path, beam_size=5, language="vi", condition_on_previous_text=False)
    segments = list(segments)
    
    # Trích xuất dữ liệu mốc thời gian (Timestamps)
    segments_data = []
    full_text_list = []
    
    total_segments = len(segments)
    if total_segments == 0:
        print("⚠️ Không có segment nào được nhận diện từ audio này.")

    print(f"🎙️ Đang bóc băng... (0/{total_segments} - 0%)")
    last_reported_percent = -1
    for idx, segment in enumerate(segments, start=1):
        start_time = round(segment.start, 2)
        end_time = round(segment.end, 2)
        text = segment.text.strip()
        
        segments_data.append({
            "start": start_time,
            "end": end_time,
            "text": text
        })
        full_text_list.append(text)
        if total_segments > 0:
            percent = int((idx / total_segments) * 100)
            # Chỉ in khi tăng thêm 5% hoặc đã hoàn tất để log dễ đọc.
            if percent == 100 or percent // 5 > last_reported_percent // 5:
                print(f"   ↳ Tiến độ segment: {idx}/{total_segments} ({percent}%)")
                last_reported_percent = percent
        
    print("✅ Bóc băng xong!")
        
    final_output = {
        "full_text": " ".join(full_text_list),
        "segments": segments_data
    }
    
    # Lưu file chứa Timestamps
    file_name = os.path.basename(audio_path)
    base_name = os.path.splitext(file_name)[0]
    
    # Path phải được tính gộp dựa trên thư mục chạy hiện tại (bắt đầu từ data/)
    rel_path = os.path.relpath(os.path.dirname(audio_path), DATA_DIR)
    target_transcript_dir = os.path.join(TRANSCRIPT_DIR, rel_path)
    os.makedirs(target_transcript_dir, exist_ok=True)
    
    output_path = os.path.join(target_transcript_dir, f"{base_name}.json")
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_output, f, ensure_ascii=False, indent=4)
        
    print(f"[3] HOÀN THÀNH! Đã lưu tự động Subtitle và Mốc thời gian tại: {output_path}")
    print("-" * 50)

if __name__ == "__main__":
    import glob
    print("🔍 Đang tìm các audio đã được cắt (trong các thư mục có đuôi _split)...")
    
    # Hỗ trợ nhận diện các file âm thanh đa định dạng (mp3, m4a, wav) từ các script khác nhau
    supported_formats = ('*.mp3', '*.m4a', '*.wav')
    audio_files = []
    for fmt in supported_formats:
        # Tìm đệ quy trong tất cả các thư mục con có chứa "_split" nằm trong DATA_DIR
        audio_files.extend(glob.glob(os.path.join(DATA_DIR, '*_split', '**', fmt), recursive=True))

    if not audio_files:
        print(f"❌ Không tìm thấy file âm thanh nào trong các thư mục *_split! Bạn đã chạy audio_splitter.py chưa?")
    else:
        total_files = len(audio_files)
        processed_files = 0

        for idx, audio_path in enumerate(audio_files, start=1):
            file_name = os.path.basename(audio_path)
            overall_percent = int((idx / total_files) * 100)
            print(f"\n📁 Tiến độ tổng transcript: {idx}/{total_files} ({overall_percent}%) - {file_name}")
            
            # Tạo cùng cấu trúc folder trong thư mục transcripts
            rel_path = os.path.relpath(os.path.dirname(audio_path), DATA_DIR)
            target_transcript_dir = os.path.join(TRANSCRIPT_DIR, rel_path)
            os.makedirs(target_transcript_dir, exist_ok=True)
            
            transcript_path = os.path.join(target_transcript_dir, f"{os.path.splitext(file_name)[0]}.json")
            
            # Nếu chưa có file sub thì mới chạy
            if not os.path.exists(transcript_path):
                # Nâng lên 'medium' vì bạn có RTX 5060, tiếng Việt sẽ cực chuẩn
                try:
                    transcribe_audio(audio_path, model_size="medium")
                    processed_files += 1
                except Exception as e:
                    print(f"❌ Lỗi file (Có thể audio bị hỏng): {file_name}. Bỏ qua!")
            else:
                print(f"⏩ Bỏ qua {file_name} - Đã có Subtitle.")

        print(f"\n🎯 Hoàn tất vòng lặp transcript. File mới được tạo: {processed_files}/{total_files}")