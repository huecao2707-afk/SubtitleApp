import google.generativeai as genai
import os
import time
import re

class LLMProcessor:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            print("Cảnh báo: Chưa có API Key cho LLM.")
            return
            
        genai.configure(api_key=self.api_key)
        # Sửa thành model 2.0 hoặc 1.5 tùy gói bạn đang dùng
        self.model = genai.GenerativeModel('models/gemini-3.5-flash')
        print("--- [Module C] Khởi tạo thành công LLM Processor ---")

    def correct_transcript(self, raw_transcript, chunk_size=30, language="vi"):
        if not raw_transcript:
            return []
        print(f"\n--- [Module C] Gửi dữ liệu cho LLM hiệu đính (Ngôn ngữ: {language.upper()}) ---")
        final_corrected = []

        for i in range(0, len(raw_transcript), chunk_size):
            chunk = raw_transcript[i:i + chunk_size]
            print(f"  -> Đang xử lý phần {i//chunk_size + 1} (Từ câu {i} đến {i+len(chunk)-1})...")
            
            # BƯỚC CẢI TIẾN: Gắn ID vào từng dòng để AI không bị trượt
            numbered_texts = []
            for idx, item in enumerate(chunk):
                numbered_texts.append(f"[{idx}] {item['Original_Text']}")
            raw_text_chunk = "\n".join(numbered_texts)
            
            prompt = f"""
            Bạn là chuyên gia ngôn ngữ. Hãy sửa lỗi chính tả và làm mượt phụ đề (ngôn ngữ: '{language}').
            
            QUY TẮC SỐNG CÒN:
            1. BẮT BUỘC giữ nguyên cấu trúc thẻ [ID] ở đầu mỗi câu. Không tự ý thay đổi số ID.
            2. Không gộp 2 câu thành 1. Không tách 1 câu thành 2.
            3. Tuyệt đối không thêm văn bản giải thích.
            
            VĂN BẢN GỐC:
            {raw_text_chunk}
            """

            try:
                response = self.model.generate_content(prompt)
                
                # BƯỚC CẢI TIẾN: Dùng Regex để bóc tách ID và Text một cách chuẩn xác
                corrected_dict = {}
                for line in response.text.strip().split('\n'):
                    # Tìm chuỗi có dạng [số] theo sau là nội dung
                    match = re.match(r'\[(\d+)\]\s*(.*)', line.strip())
                    if match:
                        idx = int(match.group(1))
                        text = match.group(2)
                        corrected_dict[idx] = text
                
                # Kiểm tra: Nếu AI trả về thiếu dòng nào, dùng lại dòng gốc của dòng đó
                for j in range(len(chunk)):
                    if j in corrected_dict and corrected_dict[j].strip():
                        chunk[j]['Original_Text'] = corrected_dict[j]
                    else:
                        print(f"      + AI nuốt mất dòng [{j}], dùng lại bản thô.")
                        
                final_corrected.extend(chunk)
                time.sleep(15) # Nghỉ để không bị limit API
                
            except Exception as e:
                print(f"  -> [Lỗi API] phần {i//chunk_size + 1}: {e}. Dùng bản thô.")
                final_corrected.extend(chunk)
                time.sleep(10)

        print("--- [Module C] Hiệu đính hoàn tất ---")
        return final_corrected

    def export_to_srt(self, transcript, output_path="output.srt"):
        def format_time(seconds):
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            millis = int((seconds - int(seconds)) * 1000)
            return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

        with open(output_path, "w", encoding="utf-8") as f:
            for idx, item in enumerate(transcript, 1):
                start = format_time(item['Start_time'])
                end = format_time(item['End_time'])
                text = item['Original_Text']
                f.write(f"{idx}\n{start} --> {end}\n{text}\n\n")
        print(f"\n--- [Hoàn thành] Đã xuất file phụ đề tại: {output_path} ---")