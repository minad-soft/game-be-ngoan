import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import os

DB_URL = 'https://game-be-ngoan-default-rtdb.asia-southeast1.firebasedatabase.app/'
KEY_FILE = 'firebase_key.json'

def migrate():
    print("Khởi tạo kết nối Firebase...")
    cred = credentials.Certificate(KEY_FILE)
    firebase_admin.initialize_app(cred, {
        'databaseURL': DB_URL
    })

    print("Đọc dữ liệu từ database.json...")
    if not os.path.exists('database.json'):
        print("Không tìm thấy file database.json. Quá trình dừng lại.")
        return
        
    with open('database.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("Đang đẩy dữ liệu lên Firebase Realtime Database...")
    ref = db.reference('/')
    ref.set(data)
    
    print("✅ Đã đẩy dữ liệu thành công!")

if __name__ == "__main__":
    migrate()
