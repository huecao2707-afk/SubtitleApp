# Module B (Speech-to-Text - Whisper)
import os
import whisper
import torch

class AIEngine:
    def __init__(self,model_size="base"):
        ffmpeg_path = os.getcwd() 
        if ffmpeg_path not in os.environ["PATH"]:
            os.environ["PATH"] += os.pathsep + ffmpeg_path
        'Khởi tạo AI Engine'
        # Kiểm tra xem có card đồ họa NVIDIA (CUDA) không để tăng tốc
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Load mode Whisper
        print(f"--- Đang tải mode Whisper [{model_size}] trên {self.device} ---")
        try:
            self.model = whisper.load_model(model_size,device=self.device)
            print("--- Tải model thành công  ---")
        except Exception as e:
            print(f"Lỗi khi tải model")
            self.model = None

    def transcribe_audio(self,audio_path):
        if self.model is None:
            print("Lỗi : Model chưa được khởi tạo")
            return []
        
        'Thực hiện nhận diện giọng nói và trả về dữ liệu kèm timestamp'
        if not os.path.exists(audio_path):
            return f"Lỗi: không tìm thấy file {audio_path}"
        print(f"--- Đang xử lý âm thanh: {os.path.basename(audio_path)} ---")

        use_fp16 = True if self.device == "cuda" else False

        # Chạy nhận diện
        # Whisper tự động nhận diện Language Detection
        try:
            result = self.model.transcribe(audio_path, verbose = False, fp16 = use_fp16)

            # In ra ngôn ngữ đã nhận diện cho người dùng biết
            detected_lang = result.get("language", "Không xác định")
            print(f"--- Ngôn ngữ nhận diện được: {detected_lang.upper()} ---")

            # Cấu trúc đầu ra
            transcription_output = []

            for segment in result["segments"]:
                item = {
                    "Start_time": round(segment["start"] , 2),
                    "End_time": round(segment["end"] , 2),
                    "Original_Text": segment["text"].strip()
                }
                transcription_output.append(item)
            return transcription_output
        except Exception as e:
            print(f"Lỗi trong quá trình nhận diện: {e}")
            return []
