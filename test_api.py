import google.generativeai as genai

# Thay bằng API KEY thật của bạn
genai.configure(api_key="AIzaSyAHUyCQRfmjgYYjsrTtondn5ls1a6FpB7I")

print("Danh sách các model AI bạn có thể dùng:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)