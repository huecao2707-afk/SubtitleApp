import re
from typing import Any, Dict, List
import logging

logger = logging.getLogger(__name__)

def safe_float(val, default=0.0):
    try: return float(val)
    except Exception: return default

def optimize_whisper_segments(raw_segments: List[Dict[str, Any]], max_chars: int = 42, max_dur: float = 3.5) -> List[Dict[str, Any]]:
    all_words = []
    for seg in raw_segments:
        for w in seg.get('words', []):
            if 'word' in w:
                s_t = safe_float(w.get('start', 0.0))
                e_t = max(s_t, safe_float(w.get('end', s_t)))
                # Chuẩn hóa từ: Xóa ký tự xuống dòng rác
                word_clean = w['word'].strip().replace('\n', ' ')
                all_words.append({'start': s_t, 'end': e_t, 'word': word_clean})
                
    if not all_words:
        return [
            {
                "Start_time": safe_float(seg.get("start", 0.0)),
                "End_time": safe_float(seg.get("end", 0.0)),
                "Original_Text": seg.get("text", "").strip().replace('\n', ' ')
            } for seg in raw_segments
        ]

    # TỐI ƯU 1: Sort theo start time để chống rối loạn timestamps từ Whisper
    all_words.sort(key=lambda x: x['start'])

    # TỐI ƯU 2: Đảm bảo Monotonic (không lùi thời gian và không lồng ghép chồng chéo)
    for i in range(1, len(all_words)):
        if all_words[i]['start'] < all_words[i-1]['end']:
            all_words[i]['start'] = all_words[i-1]['end']
        if all_words[i]['end'] < all_words[i]['start']:
            all_words[i]['end'] = all_words[i]['start']

    blocks = []
    cur_words = []
    punct_re = re.compile(r"[.!?。！？]+\s*$")
    comma_re = re.compile(r"[,،、]+\s*$")

    def flush():
        if not cur_words: return
        start_t = cur_words[0]['start']
        end_t = cur_words[-1]['end']
        text = " ".join([w['word'] for w in cur_words]).strip()
        if text:
            blocks.append({"Start_time": start_t, "End_time": end_t, "Original_Text": text})
        cur_words.clear()

    for w in all_words:
        if not w['word']: continue
        
        temp_text = " ".join([cw['word'] for cw in cur_words] + [w['word']]).strip()
        temp_dur = w['end'] - cur_words[0]['start'] if cur_words else w['end'] - w['start']
        
        is_strong_punct = bool(punct_re.search(w['word']))
        is_comma = bool(comma_re.search(w['word']))
        
        if cur_words and (len(temp_text) > max_chars or temp_dur > max_dur):
            flush()
            cur_words.append(w)
            if is_strong_punct: flush()
            continue
            
        cur_words.append(w)
        if is_strong_punct:
            flush()
        elif is_comma and temp_dur > 2.0:
            flush()
            
    flush() 
    return blocks