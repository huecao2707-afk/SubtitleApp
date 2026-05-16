# SubtitleApp

Bước 1: Khởi tạo môi trường ảo (Virtual Environment)
Việc này giúp cô lập các thư viện của dự án, tránh xung đột với hệ thống.

    Mở Terminal trong thư mục dự án.
    Chạy lệnh:

    python -m venv whisper_env

    Kích hoạt môi trường ảo (Sau khi chạy, bạn sẽ thấy chữ (whisper_env) ở đầu dòng lệnh):

    Ở bước này phải cài bản python chính thống thì khi mở folder ảo lên sẽ thấy folder Scripts mới đúng còn nếu là bin thì phải tải lại bản chính thống
    source whisper_env/Scripts/activate


    Bước 2: Cài đặt công cụ FFmpeg (Bắt buộc)
    Whisper cần FFmpeg để xử lý âm thanh từ video. Vì file .exe quá nặng không nên đưa lên GitHub, bạn cần cài vào máy:

Tải bản nén tại: https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z

Giải nén và copy đường dẫn của thư mục bin (ví dụ: C:\ffmpeg\bin).

Thêm đường dẫn đó vào Environment Variables (Path) của Windows.

Kiểm tra: Gõ ffmpeg -version trong terminal, nếu hiện thông tin là thành công.

Bước 3: Cài đặt các thư viện Python cần thiết
Sau khi đã ở trong môi trường ảo (whisper_env), hãy lần lượt chạy các lệnh sau:

Cài đặt thư viện AI Whisper:

Bash
pip install -U openai-whisper
Cài đặt bộ xử lý âm thanh và video:

Bash
pip install pydub moviepy
Cài đặt giao diện (nếu bạn dùng CustomTkinter):

Bash
pip install customtkinter
Cài đặt hỗ trợ hệ thống:

Bash
pip install setuptools-rust
(Hoặc nếu bạn đã có file requirements.txt, chỉ cần chạy duy nhất lệnh: pip install -r requirements.txt)

Bước 4: Kiểm tra và Chạy chương trình
Đảm bảo file video/audio đầu vào của bạn nằm đúng thư mục hoặc đúng đường dẫn trong code.

Chạy file chính của dự án:

Bash
python main.py
