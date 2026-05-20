# Module A (Xử lý Video/Audio/FFmpeg)
# Module A (Xử lý Video/Audio/FFmpeg)
import os
import subprocess

class MediaProcessor:
    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        # Đảm bảo thư mục output luôn tồn tại
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def extract_vocals_with_demucs(self, video_path):
        """
        Trích xuất và lọc sạch nhạc nền khỏi video, chỉ giữ lại giọng nói.
        """
        if not os.path.exists(video_path):
            print(f"Lỗi: Không tìm thấy video {video_path}")
            return None

        print(f"\n--- [Module A] Bắt đầu dùng Demucs lọc tạp âm cho: {os.path.basename(video_path)} ---")
        
        try:
            command = [
                "demucs",
                "-n", "htdemucs", 
                "--two-stems=vocals", 
                "--float32",
                video_path,
                "-o", self.output_dir
            ]
            
            # Chạy tiến trình tách âm
            subprocess.run(command, check=True)
            
            # Cấu trúc thư mục mặc định của Demucs
            base_name = os.path.splitext(os.path.basename(video_path))[0]
            vocal_path = os.path.join(self.output_dir, "htdemucs", base_name, "vocals.wav")
            
            if os.path.exists(vocal_path):
                print(f"--- [Module A] Lọc thành công! Âm thanh sạch tại: {vocal_path} ---")
                return vocal_path
            else:
                return None
                
        except Exception as e:
            print(f"--- [Module A] Lỗi khi xử lý âm thanh: {e} ---")
            return None