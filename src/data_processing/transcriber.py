import os
import json
import whisper
import warnings

# Tắt cảnh báo FP16 trên CPU (nếu không có GPU)
warnings.filterwarning("ignore", message="FP16 is not supported on CPU; using FP32 instead")

# Thiết lập đường dẫn thư mục
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
AUDIO_DIR = os.path.join(DATA_DIR, "raw_audio")
TRANSCRIPT_DIR = os.path.join(DATA_DIR, "transcripts")

os.makedirs(TRANSCRIPT_DIR, exist_ok=True)

def transcribe_audio(audio_path: str, model_size: str = "small"):
    """
    Sử dụng OpenAI Whisper để tự động tạo phụ đề (Subtitles) 
    và lấy Timestamps từ file Audio.
    """
    print(f"\n[1] Đang tải mô hình AI Whisper (Size: {model_size})...")
    # Các size: tiny, base, small, medium, large. 
    # 'small': Cân bằng tốt giữa tốc độ và độ chính xác cho Tiếng Việt.
    model = whisper.load_model(model_size)
    
    file_name = os.path.basename(audio_path)
    print(f"[2] Bắt đầu nghe và tạo Subtitle cho: {file_name}")
    print("    Quá trình này có thể mất vài phút tùy vào cấu hình máy tính (GPU/CPU)...")
    
    # Chạy AI Transcribe, ép ngôn ngữ Tiếng Việt để chạy nhanh hơn
    result = model.transcribe(audio_path, language="vi", fp16=False)
    
    # Lưu file chứa Timestamps
    file_name = os.path.basename(audio_path)
    base_name = os.path.splitext(file_name)[0]
    
    # Path phải được tính gộp dựa trên thư mục chạy hiện tại
    rel_path = os.path.relpath(os.path.dirname(audio_path), AUDIO_DIR)
    target_transcript_dir = os.path.join(TRANSCRIPT_DIR, rel_path)
    os.makedirs(target_transcript_dir, exist_ok=True)
    
    output_path = os.path.join(target_transcript_dir, f"{base_name}.json")
    
    # Trích xuất dữ liệu mốc thời gian (Timestamps)
    segments_data = []
    for segment in result["segments"]:
        segments_data.append({
            "start": round(segment["start"], 2), # Thời điểm bắt đầu câu (giây)
            "end": round(segment["end"], 2),     # Thời điểm kết thúc câu (giây)
            "text": segment["text"].strip()      # Nội dung câu nói
        })
        
    final_output = {
        "full_text": result["text"].strip(),
        "segments": segments_data
    }
        
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_output, f, ensure_ascii=False, indent=4)
        
    print(f"[3] HOÀN THÀNH! Đã lưu tự động Subtitle và Mốc thời gian tại: {output_path}")
    print("-" * 50)
    
    # In thử 3 câu đầu tiên ra màn hình cho vui
    print("🎙️ Trích đoạn Audio:")
    for s in segments_data[:3]:
        print(f"[{s['start']}s -> {s['end']}s] {s['text']}")
    print("...")

if __name__ == "__main__":
    import glob
    # Chạy đệ quy tìm tất cả file âm thanh trong máy (cả .mp3 và các dạng .m4a nếu có)
    if not os.path.exists(AUDIO_DIR):
        print(f"❌ Không tìm thấy thư mục {AUDIO_DIR}. Hãy chạy Crawler trước!")
    else:
        # Hỗ trợ nhận diện các file âm thanh đa định dạng (mp3, m4a, wav) từ các script khác nhau
        supported_formats = ('*.mp3', '*.m4a', '*.wav')
        audio_files = []
        for fmt in supported_formats:
            audio_files.extend(glob.glob(os.path.join(AUDIO_DIR, '**', fmt), recursive=True))

        if not audio_files:
            print(f"❌ Không tìm thấy file âm thanh nào bên trong {AUDIO_DIR}!")
        else:
            for audio_path in audio_files:
                file_name = os.path.basename(audio_path)
                
                # Tạo cùng cấu trúc folder trong thư mục transcripts
                rel_path = os.path.relpath(os.path.dirname(audio_path), AUDIO_DIR)
                target_transcript_dir = os.path.join(TRANSCRIPT_DIR, rel_path)
                os.makedirs(target_transcript_dir, exist_ok=True)
                
                transcript_path = os.path.join(target_transcript_dir, f"{os.path.splitext(file_name)[0]}.json")
                
                # Nếu chưa có file sub thì mới chạy
                if not os.path.exists(transcript_path):
                    transcribe_audio(audio_path, model_size="small")
                else:
                    print(f"⏩ Bỏ qua {file_name} - Đã có Subtitle.")