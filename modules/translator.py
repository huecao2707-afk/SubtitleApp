# Module C (Dịch thuật & Định dạng SRT)
from deep_translator import GoogleTranslator
import os


class SubtitleTranslator:
    def __init__(self, target_language="vi"):
        self.translator = GoogleTranslator(
            source='auto',
            target=target_language
        )
        self.target_language = target_language

    def translate_segments(self, segments):
        """
        Nhận list subtitle từ AIEngine
        và trả về subtitle đã dịch
        """

        translated_segments = []

        print("\n--- Đang dịch phụ đề sang tiếng Việt ---")

        for segment in segments:
            try:
                translated = self.translator.translate(
                    segment["Original_Text"]
                )

                item = {
                    "Start_time": segment["Start_time"],
                    "End_time": segment["End_time"],
                    "Translated_Text": translated
                }

                translated_segments.append(item)

                print(f"{segment['Original_Text']} -> {translated}")

            except Exception as e:
                print(f"Lỗi dịch: {e}")

        return translated_segments

    def format_timestamp(self, seconds: float):
        """
        Chuyển đổi giây sang định dạng SRT
        HH:MM:SS,mmm
        """

        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds - int(seconds)) * 1000)

        return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"

    def save_to_srt(self, data, output_path):
        """
        Xuất file .srt
        """

        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            with open(output_path, "w", encoding="utf-8") as f:

                for i, item in enumerate(data, start=1):

                    start = self.format_timestamp(item["Start_time"])
                    end = self.format_timestamp(item["End_time"])
                    text = item["Translated_Text"]

                    f.write(f"{i}\n")
                    f.write(f"{start} --> {end}\n")
                    f.write(f"{text}\n\n")

            print(f"\n--- Đã lưu file SRT tại: {output_path} ---")

        except Exception as e:
            print(f"Lỗi lưu file SRT: {e}")
