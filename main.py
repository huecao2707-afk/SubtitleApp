# File chạy chính (Kết nối 3 module)
import os

FFMPEG_DLL_DIR = os.path.join(os.path.dirname(__file__), "ffmpeg_lib")
# Chỉ dùng cơ chế add_dll_directory trên Windows.
if os.path.isdir(FFMPEG_DLL_DIR):
    if hasattr(os, "add_dll_directory"):
        os.add_dll_directory(FFMPEG_DLL_DIR)

    # Cập nhật PATH để cả subprocess (demucs/ffmpeg) cũng tìm được DLL phụ thuộc.
    os.environ["PATH"] = FFMPEG_DLL_DIR + os.pathsep + os.environ.get("PATH", "")
else:
    print(f"[FFmpeg] Chưa thấy folder DLL: {FFMPEG_DLL_DIR}")

from modules.media_processor import MediaProcessor # Nạp Module 1
from modules.ai_engine import AIEngine           # Nạp Module 2
def main():
    video_input = "input/file1.mp4" 
    
    # ==========================================
    # CHẠY MODULE 1: RÚT TRÍCH VÀ LỌC ÂM THANH
    # ==========================================
    media_mod = MediaProcessor()
    # Truyền mp4 vào, nhận lại wav sạch
    clean_audio_path = media_mod.extract_vocals_with_demucs(video_input) 
    
    if not clean_audio_path:
        print("Dừng chương trình: Không có âm thanh để xử lý.")
        return

    # ==========================================
    # CHẠY MODULE 2: AI NHẬN DIỆN GIỌNG NÓI
    # ==========================================
    ai_mod = AIEngine(model_size="small") # Dùng model small int8 cho nhanh
    
    # Truyền file wav sạch (chỉ có giọng người) vào cho AI nghe
    subtitles_data = ai_mod.transcribe_audio(clean_audio_path)
    
    # ==========================================
    # TẠM THAY THẾ MODULE 3: IN KẾT QUẢ
    # ==========================================
    if subtitles_data:
        print("\n=== KẾT QUẢ NHẬN DIỆN ===")
        for sub in subtitles_data:
            print(f"[{sub['Start_time']}s -> {sub['End_time']}s] {sub['Original_Text']}")

if __name__ == "__main__":
    main()