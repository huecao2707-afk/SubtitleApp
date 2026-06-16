import os
import subprocess
import logging

logger = logging.getLogger(__name__)

class MediaProcessor:
    def __init__(self, vocal_dir="vocal"):
        self.vocal_dir = vocal_dir
        if not os.path.exists(self.vocal_dir):
            os.makedirs(self.vocal_dir)

    def extract_vocals_with_demucs(self, video_path):
        if not os.path.exists(video_path):
            logger.error(f"Lỗi: Không tìm thấy video {video_path}")
            return None

        base_name = os.path.splitext(os.path.basename(video_path))[0]
        expected_vocal_path = os.path.join(self.vocal_dir, "htdemucs", base_name, "vocals.wav")

        if os.path.exists(expected_vocal_path):
            logger.info("--- [TẦNG 1] ⏭️ Đã có sẵn audio sạch. Bỏ qua Demucs! ---")
            return expected_vocal_path

        logger.info(f"--- [TẦNG 1] Bắt đầu dùng Demucs cho: {os.path.basename(video_path)} ---")
        
        try:
            command = ["demucs", "-n", "htdemucs", "--two-stems=vocals", "--float32", video_path, "-o", self.vocal_dir]
            
            # Chụp log lỗi nếu ffmpeg/codec fail
            result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=1800)
            
            if os.path.exists(expected_vocal_path):
                logger.info(f"--- [TẦNG 1] Âm thanh sạch tại: {expected_vocal_path} ---")
                return expected_vocal_path
            else:
                logger.error("--- [TẦNG 1] Lỗi: Demucs chạy xong nhưng không xuất ra vocals.wav ---")
                return None

        except subprocess.CalledProcessError as e:
            logger.error(f"--- [TẦNG 1] Lỗi Demucs Crashed: {e.stderr} ---")
            return None
        except Exception as e:
            logger.error(f"--- [TẦNG 1] Lỗi không xác định: {e} ---")
            return None