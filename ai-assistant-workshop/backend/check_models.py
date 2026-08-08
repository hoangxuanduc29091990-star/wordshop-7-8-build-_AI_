import os
from google import genai
from dotenv import load_dotenv

# Nạp API Key từ file .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

try:
    client = genai.Client(api_key=api_key)
    print("Danh sách các mô hình Gemini khả dụng cho API Key của bạn:")
    print("-" * 50)
    
    # Lấy danh sách model từ Google
    models = client.models.list()
    for m in models:
        # Chỉ in ra các mô hình có chữ 'gemini'
        if "gemini" in m.name.lower():
            print(f"👉 Tên chuẩn: {m.name}")
            
except Exception as e:
    print("Lỗi khi lấy danh sách mô hình:", e)