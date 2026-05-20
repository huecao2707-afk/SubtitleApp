# File chạy chính (Kết nối 3 module)
import os
from modules.ai_engine import AIEngine
from modules.translator import SubtitleTranslator
def format_timestamp(seconds: float):
    'Chuyển đổi giây sang định dạng srt: HH,MM,SS,mmm'
    td_hours = int(seconds //3600)
    td_minutes = int((seconds % 3600) // 60)
    td_seconds = int(seconds % 60)
    td_milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{td_hours:02}:{td_minutes:02}:{td_seconds:02},{td_milliseconds:03}"

def save_to_srt(data,output_path):
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok = True)
        with open(output_path, "w" ,encoding="utf-8") as f:
            for i, item in enumerate(data, start= 1):
                start = format_timestamp(item['Start_time'])
                end = format_timestamp(item['End_time'])
                text = item['Original_Text']
                
                f.write(f"{i}\n")
                f.write(f"{start} --> {end}\n")
                f.write(f"{text}\n\n")
        print(f"--- Đã xuất file phụ đề thành công tại: {output_path}")
    except Exception as e:
        print(f"Lỗi khi lưu file srt: {e}")
def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    audio_file = os.path.join(base_dir, "input", "test1.mp4")
    output_file = "output/result_vi.srt" # Đổi đuôi file thành .srt
    
    engine = AIEngine(model_size="base")
    results = engine.transcribe_audio(audio_file)
    print(results)
    print(type(results))

    if len(results) > 0:
        print(type(results[0]))
    
    if results:

        # Khởi tạo translator
        target_lang = "vi"  # sau này lấy từ UI

        translator = SubtitleTranslator(
            target_language=target_lang
        )

        # Dịch subtitle
        translated_results = translator.translate_segments(results)

        # Xuất file SRT tiếng Việt
        translator.save_to_srt(
            translated_results,
            output_file
        )

    else:
        print("Không có dữ liệu để xuất phụ đề.")

if __name__ == "__main__":
    main()
