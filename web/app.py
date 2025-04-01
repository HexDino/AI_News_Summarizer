from flask import Flask, render_template, jsonify
import requests
from datetime import datetime, timedelta
import threading
import time
import sys
import os

# Thêm thư mục gốc vào PYTHONPATH để import các module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.news_crawler import crawl_all_news
from models.summarizer import summarize_news

app = Flask(__name__)

# Biến global để lưu trữ thời gian cập nhật cuối cùng
last_update = None
update_interval = 30 * 60  # 30 phút

def update_news_periodically():
    """Hàm cập nhật tin tức định kỳ"""
    global last_update
    while True:
        try:
            print("Bắt đầu cập nhật tin tức...")
            # Crawl tin tức mới từ các nguồn
            crawl_all_news()
            # Tóm tắt tin tức
            summarize_news()
            last_update = datetime.now()
            print(f"Đã cập nhật tin tức lúc: {last_update}")
        except Exception as e:
            print(f"Lỗi khi cập nhật tin tức: {str(e)}")
        
        # Đợi đến lần cập nhật tiếp theo
        time.sleep(update_interval)

@app.route("/")
def home():
    try:
        # Lấy danh sách categories
        categories_response = requests.get("http://127.0.0.1:8000/categories")
        categories = categories_response.json()["categories"]
        
        # Lấy danh sách sources
        sources_response = requests.get("http://127.0.0.1:8000/sources")
        sources = sources_response.json()["sources"]
        
        # Lấy tin tức từ API
        response = requests.get("http://127.0.0.1:8000/news")
        if response.status_code == 200:
            data = response.json()
            return render_template(
                "index.html",
                news_list=data["news"],
                categories=categories,
                sources=sources,
                last_update=last_update
            )
        else:
            error_msg = f"Lỗi khi lấy tin tức: {response.status_code}"
            return render_template("error.html", error=error_msg)
            
    except requests.RequestException as e:
        error_msg = f"Không thể kết nối đến API: {str(e)}"
        return render_template("error.html", error=error_msg)
    except Exception as e:
        error_msg = f"Lỗi không xác định: {str(e)}"
        return render_template("error.html", error=error_msg)

@app.route("/status")
def status():
    """API endpoint để kiểm tra trạng thái cập nhật"""
    return jsonify({
        "status": "running",
        "last_update": last_update.isoformat() if last_update else None,
        "next_update": (last_update + timedelta(seconds=update_interval)).isoformat() if last_update else None
    })

if __name__ == "__main__":
    # Khởi động thread cập nhật tin tức
    update_thread = threading.Thread(target=update_news_periodically, daemon=True)
    update_thread.start()
    
    # Khởi động web server
    app.run(debug=True, use_reloader=False)
