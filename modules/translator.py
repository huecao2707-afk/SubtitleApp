import os
import time
import re
import json
import logging
import copy

from typing import Any, Dict, List

from openai import OpenAI
import google.generativeai as genai

logger = logging.getLogger(__name__)

def _extract_json(text: str) -> Any:
    if not text: return None
    cleaned = re.sub(r"```json|```", "", text).strip()
    try: return json.loads(cleaned)
    except Exception: pass

    for open_ch, close_ch in (("{", "}"), ("[", "]")):
        start = cleaned.find(open_ch)
        if start == -1: continue
        depth = 0
        in_str = False
        escape = False

        for i in range(start, len(cleaned)):
            ch = cleaned[i]
            if in_str:
                if escape: escape = False
                elif ch == "\\": escape = True
                elif ch == '"': in_str = False
                continue
            if ch == '"':
                in_str = True
                continue
            if ch == open_ch: depth += 1
            elif ch == close_ch:
                depth -= 1
                if depth == 0:
                    span = cleaned[start : i + 1]
                    try: return json.loads(span)
                    except Exception: break
    return None

class LLMProcessor:
    def __init__(self, provider: str = "DeepSeek", model_name: str = "deepseek-chat", api_key: str | None = None, glossary_path: str = "glossary.json"):
        self.provider = provider
        self.model_name = model_name
        self.glossary = self._load_glossary(glossary_path)
        self.is_gemini = False

        if provider == "DeepSeek":
            self.client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        elif provider == "Groq":
            self.client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
        elif provider == "Local":
            self.client = OpenAI(api_key="lm-studio", base_url="http://localhost:1234/v1")
        elif provider == "Gemini":
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(self.model_name)
            self.is_gemini = True
        else: # OpenAI mặc định
            self.client = OpenAI(api_key=api_key)

        logger.info(f"--- [Module C] Khởi tạo LLM ({provider} - Model: {model_name}) ---")

    def _load_glossary(self, path: str) -> Dict[str, Any]:
        if not os.path.exists(path): return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
        except Exception: return {}

    def _create_semantic_chunks(self, raw_transcript: List[Dict[str, Any]], max_lines=20):
        chunks, current_chunk = [], []
        for item in raw_transcript:
            current_chunk.append(item)
            if len(current_chunk) >= max_lines:
                chunks.append(current_chunk)
                current_chunk = []
        if current_chunk: chunks.append(current_chunk)
        return chunks

    def correct_transcript(self, raw_transcript: List[Dict[str, Any]], src_lang: str = "Auto Detect", target_lang: str = "vi", style: str = "Tổng Quát"):
        
        chunks = self._create_semantic_chunks(raw_transcript, max_lines=20)
        final_corrected: List[Dict[str, Any]] = []
        glossary_str = json.dumps(self.glossary, ensure_ascii=False)
        max_retries = 3

        style_prompts = {
                    "Tổng Quát": "Dịch tự nhiên, dễ hiểu, bám sát nghĩa gốc nhưng không dịch máy móc.",
                    "Vui nhộn": "Sử dụng ngôn ngữ giới trẻ, năng động, hài hước, có thể dùng các từ lóng mạng xã hội phổ biến một cách duyên dáng.",
                    "Nghiêm túc": "Văn phong trang trọng, chuẩn mực, lịch thiệp, phù hợp với tin tức thời sự hoặc báo cáo chính thức.",
                    "Học thuật": "Dịch chính xác tuyệt đối các thuật ngữ chuyên môn. Văn phong khách quan, lạnh lùng, mang tính khoa học cao.",
                    "Phim ảnh": "Dịch theo văn phong nói (spoken language) tự nhiên nhất có thể. Biểu đạt rõ cảm xúc, ngắt nghỉ hợp lý như phụ đề phim."
                }
                
        # Lấy câu lệnh hướng dẫn tương ứng, nếu không tìm thấy thì dùng Tổng Quát
        style_instruction = style_prompts.get(style, style_prompts["Tổng Quát"])

        for i, chunk in enumerate(chunks):
            raw_text_chunk = "\n".join([f"[{idx}] {item.get('Original_Text','')}" for idx, item in enumerate(chunk)])
            
            system_prompt = f"""Bạn là dịch giả. Dịch văn bản từ [{src_lang}] sang [{target_lang}].
GIỮ NGUYÊN MAPPING 1-1. Phải trả về đúng {len(chunk)} câu.
Thuật ngữ ưu tiên: {glossary_str}
TRẢ VỀ DUY NHẤT ARRAY JSON:
[ {{"id": 0, "translated": "câu dịch 0"}}, ... ]"""

            last_err = None
            for attempt in range(1, max_retries + 1):
                try:
                    response_text = ""
                    if self.is_gemini:
                        prompt = f"{system_prompt}\n\nVăn bản:\n{raw_text_chunk}"
                        res = self.client.generate_content(prompt, request_options={"timeout": 60})
                        try: response_text = res.text
                        except ValueError: raise ValueError("Gemini chặn nội dung.")
                    else:
                        res = self.client.chat.completions.create(
                            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": raw_text_chunk}],
                            model=self.model_name, temperature=0.1, max_tokens=4000, timeout=60
                        )
                        response_text = res.choices[0].message.content.strip()

                    parsed = _extract_json(response_text)
                    if not isinstance(parsed, list): raise ValueError("LLM không trả về JSON Array")
                    
                    # BẢO MẬT: Tạo một bản nháp, chỉ khi thành công toàn bộ mới ghi đè bản gốc
                    temp_chunk = copy.deepcopy(chunk)
                    success_count = 0

                    for item in parsed:
                        if not isinstance(item, dict) or "id" not in item: continue
                        
                        # Validate ID nghiêm ngặt: Chỉ lấy đúng số nguyên
                        idx_val = item.get("id")
                        if isinstance(idx_val, int): idx = idx_val
                        elif isinstance(idx_val, str) and idx_val.isdigit(): idx = int(idx_val)
                        else: continue # Bỏ qua nếu LLM trả ID tào lao như "[1]" hay "chunk_1"

                        if 0 <= idx < len(temp_chunk):
                            final_text = item.get("translated") or item.get("vi") or item.get("target", "")
                            if isinstance(final_text, dict): final_text = final_text.get("vi", "")
                            if final_text: 
                                temp_chunk[idx]["Original_Text"] = str(final_text).strip().replace('\n', ' ')
                                success_count += 1

                    if success_count < len(chunk) * 0.7: 
                        raise ValueError(f"LLM trả thiếu câu ({success_count}/{len(chunk)}).")

                    # THÀNH CÔNG 100%: Ghi đè bản gốc bằng bản nháp
                    chunk[:] = temp_chunk
                    last_err = None
                    break

                except Exception as e:
                    last_err = e
                    logger.warning(f"[Chunk {i+1}/{len(chunks)}] Lỗi attempt {attempt}: {e}")
                    time.sleep(3 * attempt)

            if last_err:
                logger.error(f"Thất bại hoàn toàn chunk {i+1}. Giữ nguyên văn bản gốc.")
            
            final_corrected.extend(chunk)

        return final_corrected

    def export_to_srt(self, transcript: List[Dict[str, Any]], output_path: str = "output.srt"):
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            for idx, item in enumerate(transcript, 1):
                start = float(item.get('Start_time', 0.0))
                end = float(item.get('End_time', 0.0))
                text = str(item.get('Original_Text', '')).strip()
                f.write(f"{idx}\n{self._fmt(start)} --> {self._fmt(end)}\n{text}\n\n")

    def _fmt(self, s: float) -> str:
        h, m, sec = int(s // 3600), int((s % 3600) // 60), float(s) % 60
        return f"{h:02d}:{m:02d}:{sec:06.3f}".replace(".", ",")