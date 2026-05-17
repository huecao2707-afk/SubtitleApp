# Module A (Xử lý Video/Audio/FFmpeg)
import os
import subprocess
from pathlib import Path


class MediaProcessor:
    def __init__(self, temp_dir="./temp"):
        """
        Khởi tạo Module và tạo thư mục chứa file tạm nếu chưa có.
        """
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        print(f"[Init] Khởi tạo MediaProcessor. Thư mục file tạm: {self.temp_dir}")

    def extract_audio(self, video_path: str, output_audio_name: str = "extracted_audio.wav") -> str:
        """
        CHỨC NĂNG 1: Trích xuất âm thanh chuẩn Mono, 16kHz (AI-friendly nhất)
        """
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Không tìm thấy video gốc tại: {video_path}")

        output_audio_path = self.temp_dir / output_audio_name

        print(f"\n[Audio Extraction] Đang trích xuất âm thanh từ: {video_path.name}...")

        # Lệnh FFmpeg: -ac 1 (Mono), -ar 16000 (16kHz), -y (Ghi đè nếu file tồn tại)
        command = [
            'ffmpeg', '-i', str(video_path),
            '-ac', '1',
            '-ar', '16000',
            '-y', str(output_audio_path)
        ]

        try:
            # Chạy lệnh ẩn cửa sổ dòng lệnh (stderr=subprocess.DEVNULL nếu muốn ẩn log)
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"[Thành công] Âm thanh đã được lưu tại: {output_audio_path}")
            return str(output_audio_path)
        except subprocess.CalledProcessError as e:
            print(f"[Lỗi] Không thể trích xuất âm thanh. Lỗi FFmpeg: {e}")
            raise

    def burn_hardsub(self, video_path: str, srt_path: str, output_video_path: str) -> str:
        """
        CHỨC NĂNG 2: Ép cứng phụ đề (Hardsub) vào Video
        """
        video_path = Path(video_path)
        srt_path = Path(srt_path)
        output_video_path = Path(output_video_path)

        if not video_path.exists() or not srt_path.exists():
            raise FileNotFoundError("Thiếu file Video hoặc file Phụ đề (SRT)!")

        print(f"\n[Video Synchronization] Đang tiến hành burn hardsub...")

        # FFmpeg yêu cầu đường dẫn sub phải dùng dấu gạch chéo xuôi (/) và cần trích dẫn nếu có khoảng trắng
        # Đặc biệt trên Windows, filter 'subtitles' rất nhạy cảm với đường dẫn
        srt_filter_path = str(srt_path).replace('\\', '/').replace(':', '\\:')

        # Lệnh FFmpeg sử dụng filter 'subtitles'
        command = [
            'ffmpeg', '-i', str(video_path),
            '-vf', f"subtitles='{srt_filter_path}'",
            '-c:a', 'copy',  # Copy nguyên luồng audio cũ, không cần render lại audio
            '-y', str(output_video_path)
        ]

        try:
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"[Thành công] Video hardsub đã được xuất bản tại: {output_video_path}")
            return str(output_video_path)
        except subprocess.CalledProcessError as e:
            print(f"[Lỗi] Không thể ép phụ đề. Lỗi FFmpeg: {e}")
            raise

    def cleanup_resources(self):
        """
        CHỨC NĂNG 3: Dọn dẹp toàn bộ file tạm trong thư mục temp
        """
        print(f"\n[Resource Management] Đang dọn dẹp các file tạm...")
        count = 0
        for file in self.temp_dir.glob("*"):
            try:
                if file.is_file():
                    file.unlink()
                    count += 1
            except Exception as e:
                print(f"[Cảnh báo] Không thể xóa file {file.name}: {e}")
        print(f"[Hoàn thành] Đã dọn dẹp {count} file tạm. Máy sạch bong!")


# ==========================================
# CHẠY THỬ NGHIỆM (DEMO KỊCH BẢN TRONG ĐỜI THỰC)
# ==========================================
if __name__ == "__main__":
    # Lưu ý: Máy bạn cần cài đặt sẵn FFmpeg và thêm vào Environment Variables (PATH)

    # 1. Khởi tạo module
    processor = MediaProcessor(temp_dir="./my_temp_folder")

    # Giả định đường dẫn (Bạn thay bằng file thật của bạn để test nhé)
    INPUT_VIDEO = "sample_video.mp4"
    OUTPUT_FINAL_VIDEO = "output_hardsub_video.mp4"

    # Tạo file video giả lập để test nếu bạn chưa có file thật
    if not os.path.exists(INPUT_VIDEO):
        print(f"\n[Lưu ý] Vui lòng chuẩn bị sẵn file '{INPUT_VIDEO}' trong thư mục để chạy thử.")
    else:
        try:
            # BƯỚC 1: Trích xuất âm thanh thô cho AI đọc
            audio_raw_path = processor.extract_audio(INPUT_VIDEO)

            # BƯỚC GIẢ ĐỊNH: Hệ thống AI nhận file audio -> Trả về file sub .srt
            # Đoạn này ta tự tạo 1 file srt giả lập để test chức năng 2
            FAKE_SRT = "./my_temp_folder/subtitle_demo.srt"
            with open(FAKE_SRT, "w", encoding="utf-8") as f:
                f.write("1\n00:00:01,000 --> 00:00:04,000\nXin chào, đây là phụ đề thử nghiệm!\n\n")
                f.write("2\n00:00:04,500 --> 00:00:08,000\nModule 1 xử lý đa phương tiện hoạt động tốt.")

            # BƯỚC 2: Ép phụ đề vào video
            processor.burn_hardsub(INPUT_VIDEO, FAKE_SRT, OUTPUT_FINAL_VIDEO)

        except Exception as e:
            print(f"Có lỗi xảy ra trong quá trình xử lý: {e}")

        finally:
            # BƯỚC 3: Dọn dẹp "bãi chiến trường" (Xóa file .wav và .srt tạm đi)
            # Trong thực tế, bạn có thể gọi hàm này khi user tắt app hoặc kết thúc session.
            processor.cleanup_resources()