import os
import sys
FFMPEG_DLL_DIR = os.path.join(os.path.dirname(__file__), "ffmpeg_lib")
# Chỉ dùng cơ chế add_dll_directory trên Windows.
if os.path.isdir(FFMPEG_DLL_DIR):
    if hasattr(os, "add_dll_directory"):
        os.add_dll_directory(FFMPEG_DLL_DIR)

    # Cập nhật PATH để cả subprocess (demucs/ffmpeg) cũng tìm được DLL phụ thuộc.
    os.environ["PATH"] = FFMPEG_DLL_DIR + os.pathsep + os.environ.get("PATH", "")
else:
    print(f"[FFmpeg] Chưa thấy folder DLL: {FFMPEG_DLL_DIR}")


# Import 3 module chúng ta đã xây dựng
# Lưu ý: Tên file Python phải khớp với tên bạn đã lưu (ví dụ: media_proc.py)
from modules.media_proc import MediaProcessor
from modules.ai_engine import AIEngine
from modules.translator import LLMProcessor

# BẠN CẦN ĐIỀN API KEY CỦA GEMINI VÀO ĐÂY
# Lấy miễn phí tại: https://aistudio.google.com/app/apikey
GEMINI_API_KEY = "AIzaSyAHUyCQRfmjgYYjsrTtondn5ls1a6FpB7I"

def main():
    # 1. Khai báo đường dẫn video cần xử lý
    video_path = "input/test4.mp4" # Thay bằng tên video thực tế của bạn
    
    if not os.path.exists(video_path):
        print(f"❌ Lỗi: Không tìm thấy file video '{video_path}'. Vui lòng kiểm tra lại đường dẫn!")
        sys.exit(1)

    print("="*60)
    print("🚀 KHỞI ĐỘNG HỆ THỐNG TẠO PHỤ ĐỀ (DEMUCS + WHISPER + LLM)")
    print("="*60)

    # 2. Khởi tạo các công cụ (Objects)
    print("\n[ĐANG KHỞI TẠO CÁC MODULE...]")
    media_proc = MediaProcessor(output_dir="output_audio")
    ai_engine = AIEngine(model_size="small")
    llm_proc = LLMProcessor(api_key=GEMINI_API_KEY)

    # ---------------------------------------------------------
    # BƯỚC 1: XỬ LÝ ÂM THANH
    # ---------------------------------------------------------
    print("\n" + "="*60)
    print("▶ BƯỚC 1: TÁCH ÂM THANH SẠCH BẰNG DEMUCS")
    print("="*60)
    vocal_path = media_proc.extract_vocals_with_demucs(video_path)
    
    if not vocal_path:
        print("❌ Dừng chương trình vì không trích xuất được âm thanh.")
        sys.exit(1)

    # ---------------------------------------------------------
    # BƯỚC 2: NHẬN DIỆN GIỌNG NÓI (BẢN NHÁP)
    # ---------------------------------------------------------
    print("\n" + "="*60)
    print("▶ BƯỚC 2: NHẬN DIỆN GIỌNG NÓI VỚI FASTER-WHISPER")
    print("="*60)
    raw_transcript, detected_lang = ai_engine.transcribe_audio(vocal_path)
    
    if not raw_transcript:
        print("❌ Dừng chương trình vì không nhận diện được văn bản (hoặc file âm thanh trống).")
        sys.exit(1)
    base_name = os.path.splitext(video_path)[0]
    raw_srt_path = f"{base_name}_raw_whisper.srt"
    print(f"\n[DEBUG] Đang xuất file phụ đề gốc (chưa qua sửa lỗi) tại: {raw_srt_path}")
    llm_proc.export_to_srt(raw_transcript, output_path=raw_srt_path)
    # ---------------------------------------------------------
    # BƯỚC 3: HIỆU ĐÍNH NGỮ CẢNH & XUẤT FILE
    # ---------------------------------------------------------
    print("\n" + "="*60)
    print("▶ BƯỚC 3: HIỆU ĐÍNH BẰNG LLM (GEMINI) VÀ XUẤT PHỤ ĐỀ")
    print("="*60)
    # Chia nhỏ mỗi chunk 40 câu để tránh lỗi vượt quá giới hạn token của LLM
    final_transcript = llm_proc.correct_transcript(raw_transcript, chunk_size=30, language=detected_lang)
    
    # Tạo tên file xuất ra dựa trên tên video gốc (VD: video_dau_vao_sub.srt)
    base_name = os.path.splitext(video_path)[0]
    srt_output_path = f"{base_name}_sub.srt"
    
    llm_proc.export_to_srt(final_transcript, output_path=srt_output_path)
    
    print("\n🎉 HOÀN TẤT! Toàn bộ quá trình đã xử lý xong.")

if __name__ == "__main__":
    main()