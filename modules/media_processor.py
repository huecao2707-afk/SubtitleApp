# Module A (Xử lý Video/Audio/FFmpeg)
import os
import subprocess

class MediaProcessor:
    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        # Đảm bảo thư mục output luôn tồn tại (Chức năng 3: Resource Management)
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    # Đây chính là Chức năng 1 (Audio Extraction) nhưng dùng Demucs
    def extract_vocals_with_demucs(self, video_path):
        """
        Trích xuất và lọc sạch nhạc nền khỏi video, chỉ giữ lại giọng nói.
        Trả về đường dẫn đến file âm thanh chứa giọng nói.
        """
        if not os.path.exists(video_path):
            print(f"Lỗi: Không tìm thấy video {video_path}")
            return None

        print(f"\n--- [Module 1] Bắt đầu dùng Demucs lọc tạp âm cho: {os.path.basename(video_path)} ---")
        print("--- Lưu ý: Sẽ tốn một chút thời gian để AI tách lớp âm thanh ---")
        
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
            
            # Demucs tự sinh ra đường dẫn: output/htdemucs/<tên_file>/vocals.wav
            base_name = os.path.splitext(os.path.basename(video_path))[0]
            vocal_path = os.path.join(self.output_dir, "htdemucs", base_name, "vocals.wav")
            
            if os.path.exists(vocal_path):
                print(f"--- [Module 1] Lọc thành công! Âm thanh sạch tại: {vocal_path} ---")
                return vocal_path
            else:
                return None
                
        except Exception as e:
            print(f"--- [Module 1] Lỗi khi xử lý âm thanh: {e} ---")
            return None