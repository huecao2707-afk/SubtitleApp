# File chạy chính (Kết nối 3 module)
import os
from modules.ai_engine import AIEngine
def format_timestamp(seconds: float):
    'Chuyển đổi giây sang định dạng srt: HH,MM,SS,mmm'
    td_hours = int(seconds //3600)
    td_minutes = int((seconds % 3600) // 60)
    td_seconds = int(seconds % 60)
    td_milliseconds = int(round((seconds - int(seconds) * 1000)))
    return f"{td_hours:02}:{td_minutes:02}:{td_seconds:02}:{td_milliseconds:03}"

def save_to_srt(data,output_path):
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok = True)
        with open(output_path, "w" ,encoding="utf-8") as f:
            for i, item in enumerate(data, start= 1):
                start = format_timestamp(item['Start_time'])
                end = format_timestamp(item['End_time'])
                text = item['Original_Text']
                
                f.write(f"{i}\n")
                f.write(f"{start}-->{end}\n")
                f.write(f"{text}\n\n")
        print(f"--- Đã xuất file phụ đề thành công tại: {output_path}")
    except Exception as e:
        print(f"Lỗi khi lưu file srt: {e}")
def main():
    audio_file = "input/test1.mp4" 
    output_file = "output/result.srt" # Đổi đuôi file thành .srt
    
    engine = AIEngine(model_size="base")
    results = engine.transcribe_audio(audio_file)
    
    if results:
        # Xuất ra file .srt
        save_to_srt(results, output_file)
        
        # Vẫn in ra console để theo dõi
        print("\n--- Nội dung phụ đề ---")
        for line in results:
            print(f"[{line['Start_time']}s] {line['Original_Text']}")
    else:
        print("Không có dữ liệu để xuất phụ đề.")

if __name__ == "__main__":
    main()