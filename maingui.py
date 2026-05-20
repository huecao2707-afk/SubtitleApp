import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import os
import sys
import threading
FFMPEG_DLL_DIR = os.path.join(os.path.dirname(__file__), "ffmpeg_lib")
# Chỉ dùng cơ chế add_dll_directory trên Windows.
if os.path.isdir(FFMPEG_DLL_DIR):
    if hasattr(os, "add_dll_directory"):
        os.add_dll_directory(FFMPEG_DLL_DIR)

    # Cập nhật PATH để cả subprocess (demucs/ffmpeg) cũng tìm được DLL phụ thuộc.
    os.environ["PATH"] = FFMPEG_DLL_DIR + os.pathsep + os.environ.get("PATH", "")
else:
    print(f"[FFmpeg] Chưa thấy folder DLL: {FFMPEG_DLL_DIR}")

# Import 3 Module Backend
from modules.media_proc import MediaProcessor
from modules.ai_engine import AIEngine
from modules.translator import LLMProcessor

FULL_LANGUAGES = [
    "Afrikaans", "Albanian", "Amharic", "Arabic", "Armenian", "Assamese", "Azerbaijani",
    "Bashkir", "Basque", "Belarusian", "Bengali", "Bosnian", "Breton", "Bulgarian", "Burmese",
    "Catalan", "Chinese", "Croatian", "Czech", "Danish", "Dutch", "English", "Estonian",
    "Faroese", "Finnish", "French", "Galician", "Georgian", "German", "Greek", "Gujarati",
    "Haitian Creole", "Hausa", "Hawaiian", "Hebrew", "Hindi", "Hungarian", "Icelandic", "Igbo",
    "Indonesian", "Italian", "Japanese", "Javanese", "Kannada", "Kazakh", "Khmer", "Korean",
    "Lao", "Latin", "Latvian", "Lingala", "Lithuanian", "Luxembourgish", "Macedonian", "Malagasy",
    "Malay", "Malayalam", "Maltese", "Maori", "Marathi", "Mongolian", "Nepali", "Norwegian",
    "Nynorsk", "Occitan", "Pashto", "Persian", "Polish", "Portuguese", "Punjabi", "Romanian",
    "Russian", "Sanskrit", "Serbian", "Shona", "Sindhi", "Sinhala", "Slovak", "Slovenian",
    "Somali", "Spanish", "Sundanese", "Swahili", "Swedish", "Tagalog", "Tajik", "Tamil",
    "Tatar", "Telugu", "Thai", "Tibetan", "Turkish", "Turkmen", "Ukrainian", "Urdu",
    "Uzbek", "Vietnamese", "Welsh", "Yiddish", "Yoruba"
]

class StdoutRedirector:
    """Lớp hỗ trợ chuyển hướng thông báo từ Console lên Textbox của App"""
    def __init__(self, text_widget, app):
        self.text_widget = text_widget
        self.app = app

    def write(self, string):
        if string.strip() or string == "\n":
            self.app.after(0, self._insert_text, string)

    def _insert_text(self, string):
        try:
            self.text_widget.insert("end", string)
            self.text_widget.see("end")
        except Exception:
            pass

    def flush(self):
        pass

class SubtitleAppUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AI Subtitle & Translator Engine")
        self.geometry("650x600")
        ctk.set_appearance_mode("dark")

        self.selected_file = None
        self.current_listbox = None 
        self.is_running = False

        # ==========================================
        # KHU VỰC 1: CHỌN FILE
        # ==========================================
        self.frame_file = ctk.CTkFrame(self)
        self.frame_file.pack(pady=10, padx=20, fill="x")

        self.label_file = ctk.CTkLabel(self.frame_file, text="Chưa có file nào được chọn", font=("Arial", 14))
        self.label_file.pack(pady=10)

        self.btn_browse = ctk.CTkButton(self.frame_file, text="📁 Tải file Media lên", command=self.browse_file)
        self.btn_browse.pack(pady=(0, 10))

        # ==========================================
        # KHU VỰC 2: CẤU HÌNH AI & NGÔN NGỮ
        # ==========================================
        self.frame_config = ctk.CTkFrame(self)
        self.frame_config.pack(pady=10, padx=20, fill="x")
        self.frame_config.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(self.frame_config, text="🧠 Model Whisper:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.model_var = ctk.StringVar(value="small")
        self.model_menu = ctk.CTkOptionMenu(self.frame_config, values=["tiny", "base", "small", "medium", "large"], variable=self.model_var)
        self.model_menu.grid(row=0, column=1, padx=10, pady=5, sticky="e")

        self.source_langs_full = ["Auto Detect (Tự động)"] + FULL_LANGUAGES
        ctk.CTkLabel(self.frame_config, text="🎤 Ngôn ngữ Video:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.lang_orig_var = ctk.StringVar(value=self.source_langs_full[0])
        self.create_smart_entry(self.frame_config, self.lang_orig_var, self.source_langs_full, 1, 1)

        ctk.CTkLabel(self.frame_config, text="🌐 Dịch sang:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.lang_trans_var = ctk.StringVar(value="Vietnamese")
        self.create_smart_entry(self.frame_config, self.lang_trans_var, FULL_LANGUAGES, 2, 1)

        ctk.CTkLabel(self.frame_config, text="🔑 Gemini API Key:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.api_key_var = ctk.StringVar(value="")
        self.api_entry = ctk.CTkEntry(self.frame_config, textvariable=self.api_key_var, width=200, show="*")
        self.api_entry.grid(row=3, column=1, padx=10, pady=5, sticky="e")

        # ==========================================
        # KHU VỰC 3 & 4: LOG VÀ BUTTONS
        # ==========================================
        self.textbox = ctk.CTkTextbox(self, height=150)
        self.textbox.pack(pady=10, padx=20, fill="both", expand=True)
        self.textbox.insert("0.0", "Hệ thống đã sẵn sàng...\n")

        # Chuyển hướng stdout và stderr để bắt lỗi hiện lên textbox
        sys.stdout = StdoutRedirector(self.textbox, self)
        sys.stderr = StdoutRedirector(self.textbox, self)

        self.frame_btns = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_btns.pack(pady=10)
        
        self.btn_run = ctk.CTkButton(self.frame_btns, text="✅ Bắt đầu xử lý", fg_color="#28a745", hover_color="#218838", command=self.start_process)
        self.btn_run.pack(side="left", padx=15)

        self.btn_cancel = ctk.CTkButton(self.frame_btns, text="❌ Hủy / Thoát", fg_color="#dc3545", hover_color="#c82333", command=self.quit)
        self.btn_cancel.pack(side="left", padx=15)

    def create_smart_entry(self, parent, variable, data_list, row, col):
        entry = ctk.CTkEntry(parent, textvariable=variable, width=200, placeholder_text="Gõ để tìm...")
        entry.grid(row=row, column=col, padx=10, pady=5, sticky="e")
        entry._last_valid_value = variable.get() 
        entry.bind("<FocusIn>", lambda e: self.on_focus_in(e, entry, variable, data_list))
        entry.bind("<FocusOut>", lambda e: self.on_focus_out(e, entry, variable, data_list))
        entry.bind("<KeyRelease>", lambda e: self.on_type(e, entry, variable, data_list))

    def on_focus_in(self, event, entry_widget, variable, data_list):
        current_val = variable.get()
        if current_val in data_list: entry_widget._last_valid_value = current_val
        variable.set("")
        self.on_type(None, entry_widget, variable, data_list)

    def on_focus_out(self, event, entry_widget, variable, data_list):
        def restore_state():
            if self.current_listbox:
                self.current_listbox.destroy()
                self.current_listbox = None
            if variable.get() not in data_list:
                variable.set(getattr(entry_widget, '_last_valid_value', data_list[0]))
        self.after(200, restore_state)

    def on_type(self, event, entry_widget, variable, data_list):
        if event and event.keysym in ["Up", "Down", "Return"]: return 
        typed_text = variable.get().lower()
        hits = data_list if typed_text == "" else [item for item in data_list if typed_text in item.lower()]
        self.show_dropdown(entry_widget, variable, hits, data_list)

    def show_dropdown(self, entry_widget, variable, hits, data_list):
        if self.current_listbox:
            self.current_listbox.destroy()
            self.current_listbox = None
        if not hits: return 
            
        x = entry_widget.winfo_rootx() - self.winfo_rootx()
        y = entry_widget.winfo_rooty() - self.winfo_rooty() + entry_widget.winfo_height() + 2
        width = entry_widget.winfo_width()
        
        self.current_listbox = tk.Listbox(
            self, bg="#2b2b2b", fg="white", selectbackground="#1f538d",
            font=("Arial", 12), highlightthickness=1, highlightbackground="#565b5e",
            relief="flat", height=min(6, len(hits))
        )
        self.current_listbox.place(x=x, y=y, width=width)
        for hit in hits: self.current_listbox.insert(tk.END, hit)
        self.current_listbox.bind("<<ListboxSelect>>", lambda e: self.on_select(e, variable, entry_widget, data_list))
        self.current_listbox.lift()

    def on_select(self, event, variable, entry_widget, data_list):
        if self.current_listbox.curselection():
            index = self.current_listbox.curselection()[0]
            selected_value = self.current_listbox.get(index)
            variable.set(selected_value) 
            entry_widget._last_valid_value = selected_value 
            self.current_listbox.destroy()
            self.current_listbox = None
            self.focus_set()

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Media Files", "*.mp4 *.m4a *.mp3 *.wav *.avi")])
        if file_path:
            self.selected_file = file_path
            self.label_file.configure(text=f"Đã chọn: {os.path.basename(file_path)}")
            print(f"Đã load file: {file_path}")

    def start_process(self):
        if not self.selected_file:
            print("[LỖI] Vui lòng chọn file media trước!")
            return
        if not self.api_key_var.get().strip():
            print("[LỖI] Vui lòng nhập Gemini API Key!")
            return
        if self.is_running:
            return

        self.btn_run.configure(state="disabled", text="⏳ Đang xử lý...")
        self.is_running = True

        threading.Thread(target=self.run_ai_pipeline, daemon=True).start()

    def run_ai_pipeline(self):
        try:
            model = self.model_var.get()
            source_lang = self.lang_orig_var.get()
            language = self.lang_trans_var.get()
            api_key = self.api_key_var.get().strip()

            print("\n" + "="*50)
            print("🚀 BẮT ĐẦU QUÁ TRÌNH XỬ LÝ")
            print("="*50)

            # KHỞI TẠO MODULE
            media_proc = MediaProcessor(output_dir="output_audio")
            ai_engine = AIEngine(model_size=model)
            llm_proc = LLMProcessor(api_key=api_key)

            # BƯỚC 1: Tách âm
            print("\n▶ BƯỚC 1: Tách âm thanh sạch bằng Demucs")
            vocal_path = media_proc.extract_vocals_with_demucs(self.selected_file)
            if not vocal_path:
                print("❌ Dừng lại do lỗi tách âm thanh.")
                self.btn_run.configure(state="normal", text="✅ Bắt đầu xử lý")
                self.is_running = False
                return

            # BƯỚC 2: Whisper STT
            print("\n▶ BƯỚC 2: Nhận diện giọng nói gốc")
            raw_transcript, detected_lang = ai_engine.transcribe_audio(vocal_path)
            
            if not raw_transcript:
                print("❌ Lỗi: Không nhận diện được đoạn hội thoại nào.")
                self.btn_run.configure(state="normal", text="✅ Bắt đầu xử lý")
                self.is_running = False
                return
            
            actual_source = detected_lang if "Auto Detect" in source_lang else source_lang

            # BƯỚC 3: Dịch thuật LLM
            print("\n▶ BƯỚC 3: LLM Hiệu đính & Dịch thuật")
            final_transcript = llm_proc.correct_transcript(
                raw_transcript, 
                chunk_size=20, 
                source_lang=actual_source, 
                language=language
            )

            # XUẤT FILE
            base_name = os.path.splitext(self.selected_file)[0]
            srt_output_path = f"{base_name}_sub.srt"
            llm_proc.export_to_srt(final_transcript, output_path=srt_output_path)
            
            print("\n🎉 HOÀN TẤT THÀNH CÔNG! File phụ đề đã sẵn sàng.")

        except Exception as e:
            print(f"\n❌ Đã xảy ra lỗi hệ thống: {e}")
        
        finally:
            self.btn_run.configure(state="normal", text="✅ Bắt đầu xử lý")
            self.is_running = False

if __name__ == "__main__":
    app = SubtitleAppUI()
    app.mainloop()