import os
import gc
import logging
import torch
import whisperx

logger = logging.getLogger(__name__)

class AIEngine:
    def __init__(self, model_size: str = "small"):
        self.model_size = model_size

    # Thêm tham số language_code và initial_prompt với giá trị mặc định là None
    def transcribe_audio(self, audio_path, language_code=None, initial_prompt=None):
        if not os.path.exists(audio_path): return []
        device = "cuda" if torch.cuda.is_available() else "cpu"
        compute_type = "float16" if device == "cuda" else "int8"
        model = None
        model_a = None

        try:
            with torch.no_grad():
                # Vẫn giữ VAD khắt khe để chặn tạp âm ầm ĩ
                vad_options = {"vad_onset": 0.750, "vad_offset": 0.500}
                model = whisperx.load_model(self.model_size, device=device, compute_type=compute_type, vad_options=vad_options)
                
                # Cấu hình các tham số cốt lõi chống ảo giác
                transcribe_kwargs = {
                    "batch_size": 8,
                }
                
                # Gắn thêm tham số linh hoạt nếu người dùng có truyền vào
                if language_code:
                    transcribe_kwargs["language"] = language_code
                if initial_prompt:
                    transcribe_kwargs["initial_prompt"] = initial_prompt

                # Truyền unpacking dictionary vào hàm transcribe
                result = model.transcribe(audio_path, **transcribe_kwargs)
                
                # Xác định ngôn ngữ để load model Align (ưu tiên ngôn ngữ được truyền vào, nếu không có thì lấy cái tự nhận diện)
                detected_language = language_code or result.get("language")
                if not detected_language: raise RuntimeError("Không nhận diện được ngôn ngữ.")

                model_a, metadata = whisperx.load_align_model(language_code=detected_language, device=device)
                result = whisperx.align(result["segments"], model_a, metadata, audio_path, device, return_char_alignments=False)
                
                return result["segments"]

        finally:
            if model is not None: del model
            if model_a is not None: del model_a
            gc.collect()
            if device == "cuda":
                torch.cuda.synchronize()
                torch.cuda.empty_cache()