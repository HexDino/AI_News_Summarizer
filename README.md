# AI News Summarizer

Ứng dụng thu thập, phân tích và tóm tắt tin tức tiếng Việt từ nhiều nguồn sử dụng trí tuệ nhân tạo.

## Tính năng

- Thu thập tin tức tự động từ các nguồn báo tiếng Việt (VnExpress, Tuổi Trẻ, Thanh Niên, Dân Trí, Zing News, VTV)
- Phân loại tin tức theo nhiều chủ đề (thời sự, thế giới, kinh doanh, giải trí, thể thao, khoa học, giáo dục)
- Tóm tắt nội dung bài báo sử dụng mô hình AI (BART)
- Cung cấp API để truy xuất tin tức đã được tóm tắt
- Giao diện web để hiển thị tin tức

## Cài đặt

1. Clone repository:
   ```
   git clone https://github.com/HexDino/AI_News_Summarizer.git
   cd AI_News_Summarizer
   ```

2. Cài đặt các thư viện cần thiết:
   ```
   pip install -r requirements.txt
   ```

3. Khởi động các dịch vụ:
   - API:
     ```
     cd api
     python api.py
     ```
   - Web:
     ```
     cd web
     python app.py
     ```

## Cấu trúc dự án

- `api/`: API FastAPI cung cấp endpoints để truy xuất tin tức
- `data/`: Mô-đun thu thập dữ liệu từ các nguồn tin và lưu trữ
  - `news_crawler.py`: Mã nguồn crawl tin tức từ các trang báo
  - `scraper.py`: Công cụ scraping bổ sung
  - Các file JSON chứa dữ liệu tin tức thô và đã xử lý
- `models/`: Mô hình AI để tóm tắt tin tức
  - `summarizer.py`: Triển khai mô hình tóm tắt sử dụng transformers
- `web/`: Ứng dụng web Flask để hiển thị tin tức
  - `app.py`: Mã nguồn cho web app
  - `templates/`: Templates HTML
- `static/`: Tài nguyên tĩnh (CSS, JavaScript, hình ảnh)
- `templates/`: Template HTML bổ sung
- `requirements.txt`: Danh sách các thư viện Python cần thiết

## Công nghệ sử dụng

- **Thu thập dữ liệu**: BeautifulSoup4, Requests
- **Xử lý ngôn ngữ**: NLTK, Transformers (BART)
- **API**: FastAPI, Uvicorn
- **Web**: Flask, Jinja2
- **AI/ML**: PyTorch, Hugging Face Transformers 