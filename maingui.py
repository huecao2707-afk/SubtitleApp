import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import os
from modules.ai_engine import AIEngine
from modules.translator import SubtitleTranslator

# Danh sách 99 ngôn ngữ hỗ trợ bởi Whisper
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
LANGUAGE_CODES = {
    "Vietnamese": "vi",
    "English": "en",
    "Japanese": "ja",
    "Korean": "ko",
    "Chinese": "zh-cn",
    "French": "fr",
    "German": "de",
    "Thai": "th"
}


class SubtitleAppUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AI Subtitle & Translator Engine")
        self.geometry("650x550")
        ctk.set_appearance_mode("dark")

        self.selected_file = None
        self.current_listbox = None 

        # ==========================================
        # KHU VỰC 1: CHỌN FILE
        # ==========================================
        self.frame_file = ctk.CTkFrame(self)
        self.frame_file.pack(pady=20, padx=20, fill="x")

        self.label_file = ctk.CTkLabel(self.frame_file, text="Chưa có file nào được chọn", font=("Arial", 14))
        self.label_file.pack(pady=10)

        self.btn_browse = ctk.CTkButton(self.frame_file, text="📁 Tải file Media lên (Video/Audio)", command=self.browse_file)
        self.btn_browse.pack(pady=(0, 10))

        # ==========================================
        # KHU VỰC 2: CẤU HÌNH AI & NGÔN NGỮ
        # ==========================================
        self.frame_config = ctk.CTkFrame(self)
        self.frame_config.pack(pady=10, padx=20, fill="x")
        self.frame_config.grid_columnconfigure((0, 1), weight=1)

        # 1. Chọn Model Whisper
        ctk.CTkLabel(self.frame_config, text="🧠 Model AI:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.model_var = ctk.StringVar(value="base")
        self.model_menu = ctk.CTkOptionMenu(self.frame_config, values=["tiny", "base", "small", "medium", "large"], variable=self.model_var)
        self.model_menu.grid(row=0, column=1, padx=10, pady=10, sticky="e")

        # 2. Ngôn ngữ Gốc (Của Video) - Chỉ dùng Entry
        self.source_langs_full = ["Auto Detect (Chậm hơn)"] + FULL_LANGUAGES
        ctk.CTkLabel(self.frame_config, text="🎤 Ngôn ngữ Video:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.lang_orig_var = ctk.StringVar(value=self.source_langs_full[0])
        self.create_smart_entry(self.frame_config, self.lang_orig_var, self.source_langs_full, 1, 1)

        # 3. Ngôn ngữ Đích (Muốn dịch sang) - Chỉ dùng Entry
        ctk.CTkLabel(self.frame_config, text="🌐 Dịch sang:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.lang_trans_var = ctk.StringVar(value="Vietnamese")
        self.create_smart_entry(self.frame_config, self.lang_trans_var, FULL_LANGUAGES, 2, 1)

        # ==========================================
        # KHU VỰC 3 & 4: LOG VÀ BUTTONS
        # ==========================================
        self.textbox = ctk.CTkTextbox(self, height=120)
        self.textbox.pack(pady=10, padx=20, fill="both", expand=True)
        self.textbox.insert("0.0", "Hệ thống đã sẵn sàng...\n")

        self.frame_btns = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_btns.pack(pady=10)
        
        self.btn_run = ctk.CTkButton(self.frame_btns, text="✅ Bắt đầu xử lý", fg_color="#28a745", hover_color="#218838", command=self.start_process)
        self.btn_run.pack(side="left", padx=15)

        self.btn_cancel = ctk.CTkButton(self.frame_btns, text="❌ Hủy / Thoát", fg_color="#dc3545", hover_color="#c82333", command=self.quit)
        self.btn_cancel.pack(side="left", padx=15)

    # ==========================================
    # LOGIC AUTOCOMPLETE - CHỈ DÙNG ENTRY
    # ==========================================
    def create_smart_entry(self, parent, variable, data_list, row, col):
        """Tạo ô nhập liệu thông minh tự động xổ list khi focus"""
        # Trả lại chiều rộng 200 do không còn bị nút bấm chiếm chỗ
        entry = ctk.CTkEntry(parent, textvariable=variable, width=200, placeholder_text="Gõ để tìm kiếm...")
        entry.grid(row=row, column=col, padx=10, pady=10, sticky="e")
        
        # Lưu trữ trạng thái chuẩn gần nhất
        entry._last_valid_value = variable.get() 

        # Ràng buộc sự kiện
        entry.bind("<FocusIn>", lambda e: self.on_focus_in(e, entry, variable, data_list))
        entry.bind("<FocusOut>", lambda e: self.on_focus_out(e, entry, variable, data_list))
        entry.bind("<KeyRelease>", lambda e: self.on_type(e, entry, variable, data_list))

    def on_focus_in(self, event, entry_widget, variable, data_list):
        """Khi click vào ô: Lưu giá trị chuẩn hiện tại và xoá trắng chữ để gõ/xem list"""
        current_val = variable.get()
        if current_val in data_list:
            entry_widget._last_valid_value = current_val

        variable.set("") # Xoá trắng text
        self.on_type(None, entry_widget, variable, data_list) # Mở listbox hiển thị toàn bộ

    def on_focus_out(self, event, entry_widget, variable, data_list):
        """Khi click ra ngoài: Phục hồi lại dữ liệu nếu bỏ trống hoặc nhập sai"""
        def restore_state():
            if self.current_listbox:
                self.current_listbox.destroy()
                self.current_listbox = None

            current_val = variable.get()
            if current_val not in data_list:
                variable.set(getattr(entry_widget, '_last_valid_value', data_list[0]))

        # Chờ 200ms để bắt sự kiện chọn listbox (nếu có) trước khi kiểm tra
        self.after(200, restore_state)

    def on_type(self, event, entry_widget, variable, data_list):
        """Lọc dữ liệu mỗi khi gõ phím"""
        if event and event.keysym in ["Up", "Down", "Return"]:
            return 
            
        typed_text = variable.get().lower()
        if typed_text == "":
            hits = data_list
        else:
            hits = [item for item in data_list if typed_text in item.lower()]
            
        self.show_dropdown(entry_widget, variable, hits, data_list)

    def show_dropdown(self, entry_widget, variable, hits, data_list):
        """Hiển thị danh sách gợi ý canh chuẩn theo Entry"""
        if self.current_listbox:
            self.current_listbox.destroy()
            self.current_listbox = None
            
        if not hits:
            return 
            
        # Lấy tọa độ gốc màn hình của chính cái Entry
        x = entry_widget.winfo_rootx() - self.winfo_rootx()
        y = entry_widget.winfo_rooty() - self.winfo_rooty() + entry_widget.winfo_height() + 2
        width = entry_widget.winfo_width()
        
        self.current_listbox = tk.Listbox(
            self, bg="#2b2b2b", fg="white", selectbackground="#1f538d",
            font=("Arial", 12), highlightthickness=1, highlightbackground="#565b5e",
            relief="flat", height=min(6, len(hits))
        )
        self.current_listbox.place(x=x, y=y, width=width)
        
        for hit in hits:
            self.current_listbox.insert(tk.END, hit)
            
        self.current_listbox.bind("<<ListboxSelect>>", lambda e: self.on_select(e, variable, entry_widget, data_list))
        self.current_listbox.lift()

    def on_select(self, event, variable, entry_widget, data_list):
        """Khi bấm chọn ngôn ngữ từ menu xổ xuống"""
        if self.current_listbox.curselection():
            index = self.current_listbox.curselection()[0]
            selected_value = self.current_listbox.get(index)
            
            variable.set(selected_value) 
            entry_widget._last_valid_value = selected_value 
            
            self.current_listbox.destroy()
            self.current_listbox = None
            
            # Thoát focus khỏi ô text sau khi chọn xong
            self.focus_set()

    # ==========================================
    # LOGIC NÚT BẤM CƠ BẢN
    # ==========================================
    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Media Files", "*.mp4 *.m4a *.mp3 *.wav *.avi")])
        if file_path:
            self.selected_file = file_path
            self.label_file.configure(text=f"Đã chọn: {os.path.basename(file_path)}")
            self.textbox.insert("end", f"Đã load file: {file_path}\n")
            self.textbox.see("end")

    def start_process(self):

        if not self.selected_file:
            self.textbox.insert("end", "[LỖI] Vui lòng chọn file media trước!\n")
            self.textbox.see("end")
            return

        try:
            model = self.model_var.get()
            source = self.lang_orig_var.get()
            target = self.lang_trans_var.get()

            self.textbox.insert("end", "-" * 40 + "\n")
            self.textbox.insert("end", f"Đang load AI model: {model}\n")
            self.textbox.see("end")

            # Khởi tạo AI
            engine = AIEngine(model_size=model)

            self.textbox.insert("end", "Đang nhận diện giọng nói...\n")
            self.textbox.see("end")

            # Speech to text
            results = engine.transcribe_audio(self.selected_file)

            if not results:
                self.textbox.insert("end", "[LỖI] Không nhận diện được phụ đề.\n")
                return

            # Convert tên ngôn ngữ -> code
            target_code = LANGUAGE_CODES.get(target, "vi")

            self.textbox.insert("end", f"Đang dịch sang: {target}\n")
            self.textbox.see("end")

            # Translator
            translator = SubtitleTranslator(
                target_language=target_code
            )

            translated_results = translator.translate_segments(results)

            # File output
            output_path = "output/result.srt"

            # Save SRT
            translator.save_to_srt(
                translated_results,
                output_path
            )

            self.textbox.insert("end", f"\n✅ Hoàn tất!\n")
            self.textbox.insert("end", f"Đã lưu tại: {output_path}\n")
            self.textbox.see("end")

        except Exception as e:
            self.textbox.insert("end", f"[LỖI] {e}\n")
            self.textbox.see("end")

if __name__ == "__main__":
    app = SubtitleAppUI()
    app.mainloop()
