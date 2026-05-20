# Module B (Speech-to-Text - Faster Whisper)
import os
from faster_whisper import WhisperModel
import torch

class AIEngine:
    def __init__(self, model_size="small"): 
        # Khởi tạo AI Engine với Faster-Whisper
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.compute_type = "float16" if self.device == "cuda" else "int8"
        
        print(f"--- [Module B] Đang tải model Faster-Whisper [{model_size}] trên {self.device} ---")
        try:
            self.model = WhisperModel(model_size, device=self.device, compute_type=self.compute_type)
            print("--- [Module B] Tải model thành công ---")
        except Exception as e:
            print(f"Lỗi khi tải model: {e}")
            self.model = None

    def transcribe_audio(self, audio_path):
        if self.model is None:
            print("Lỗi: Model chưa được khởi tạo")
            return [], None
        
        if not os.path.exists(audio_path):
            print(f"Lỗi: Không tìm thấy file {audio_path}")
            return [], None
            
        print(f"--- [Module B] Đang nhận diện âm thanh (vui lòng đợi): {os.path.basename(audio_path)} ---")

        try:
            # Faster-Whisper quét một lượt toàn bộ file, giữ nguyên vẹn Timestamp
            segments, info = self.model.transcribe(audio_path, beam_size=5,vad_filter=True, 
                vad_parameters=dict(min_silence_duration_ms=500))
            print(f"--- [Module B] Ngôn ngữ nhận diện được: {info.language.upper()} (Độ tin cậy: {info.language_probability:.2f}) ---")

            transcription_output = []
            
            for segment in segments:
                item = {
                    "Start_time": round(segment.start, 3),
                    "End_time": round(segment.end, 3),
                    "Original_Text": segment.text.strip()
                }
                transcription_output.append(item)
                
            return transcription_output, info.language
        except Exception as e:
            print(f"Lỗi trong quá trình nhận diện: {e}")
            return [], None