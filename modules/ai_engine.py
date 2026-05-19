# Module B (Speech-to-Text - Faster-Whisper)
import os
from faster_whisper import WhisperModel

class AIEngine:
    def __init__(self, model_size="small"):
        # Tự động chọn CPU và ép kiểu int8 để chạy nhanh
        self.device = "cpu"
        self.compute_type = "int8"
        
        print(f"--- Đang tải Faster-Whisper [{model_size}] trên {self.device} (Type: {self.compute_type}) ---")
        try:
            self.model = WhisperModel(model_size, device=self.device, compute_type=self.compute_type)
            print("--- Tải model thành công ---")
        except Exception as e:
            print(f"Lỗi khi tải model: {e}")
            self.model = None

    def transcribe_audio(self, audio_path, language="vi"):
        if self.model is None:
            print("Lỗi: Model chưa được khởi tạo")
            return []
            
        if not os.path.exists(audio_path):
            print(f"Lỗi: không tìm thấy file {audio_path}")
            return []

        print(f"--- Đang xử lý âm thanh: {os.path.basename(audio_path)} ---")

        try:
            segments, info = self.model.transcribe(
                audio_path,
                language=language,
                beam_size=5,
                word_timestamps=True, 
                vad_filter=True,
                vad_parameters=dict(threshold=0.2, min_silence_duration_ms=500, speech_pad_ms=500),
                condition_on_previous_text=False,
                temperature=(0.0, 0.2, 0.4, 0.6, 0.8, 1.0)
            )

            print(f"--- Ngôn ngữ nhận diện được: {info.language.upper()} với xác suất {info.language_probability:.2f} ---")

            transcription_output = []
            for segment in segments:
                item = {
                    "Start_time": round(segment.start, 2),
                    "End_time": round(segment.end, 2),
                    "Original_Text": segment.text.strip()
                }
                transcription_output.append(item)
                
            return transcription_output
            
        except Exception as e:
            print(f"Lỗi trong quá trình nhận diện: {e}")
            return []