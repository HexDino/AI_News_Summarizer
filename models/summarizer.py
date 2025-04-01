from transformers import pipeline
import torch
import json
import re
from typing import List, Dict, Tuple
import unicodedata
from nltk.tokenize import sent_tokenize
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from concurrent.futures import ThreadPoolExecutor
from functools import partial

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

def normalize_vietnamese(text: str) -> str:
    """Chuẩn hóa unicode cho tiếng Việt"""
    return unicodedata.normalize('NFKC', text)

def clean_text(text: str) -> str:
    """Làm sạch và chuẩn hóa text tiếng Việt"""
    # Chuẩn hóa unicode
    text = normalize_vietnamese(text)
    
    # Giữ lại các ký tự tiếng Việt và dấu câu quan trọng
    text = re.sub(r'[^\w\s\đĐơƠưƯăĂâÂêÊôÔơƠưƯáàảãạéèẻẽẹíìỉĩịóòỏõọúùủũụýỳỷỹỵÁÀẢÃẠÉÈẺẼẸÍÌỈĨỊÓÒỎÕỌÚÙỦŨỤÝỲỶỸỴ\.,!?-]', ' ', text)
    
    # Xóa khoảng trắng thừa
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_key_sentences(text: str, num_sentences: int = 2) -> str:
    """Trích xuất các câu quan trọng nhất dựa trên TF-IDF"""
    # Tách câu
    sentences = sent_tokenize(text)
    if len(sentences) <= num_sentences:
        return text
    
    # Nếu văn bản quá dài, chỉ lấy 500 từ đầu tiên
    words = text.split()
    if len(words) > 500:
        text = ' '.join(words[:500])
        sentences = sent_tokenize(text)
    
    # Tính TF-IDF nhanh hơn với ít features hơn
    vectorizer = TfidfVectorizer(max_features=500, stop_words=None)
    tfidf_matrix = vectorizer.fit_transform(sentences)
    
    # Tính điểm cho mỗi câu
    sentence_scores = []
    for i, sentence in enumerate(sentences):
        score = np.sum(tfidf_matrix[i].toarray())
        sentence_scores.append((score, i, sentence))
    
    # Chọn các câu có điểm cao nhất
    sentence_scores.sort(reverse=True)
    selected_indices = [x[1] for x in sentence_scores[:num_sentences]]
    selected_indices.sort()
    ordered_sentences = [sentences[i] for i in selected_indices]
    
    return ' '.join(ordered_sentences)

class NewsSummarizer:
    def __init__(self):
        # Khởi tạo model và tokenizer
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Sử dụng thiết bị: {self.device}")
        
        # Tạo pipeline với mô hình nhỏ hơn và nhanh hơn
        try:
            self.summarizer = pipeline(
                "summarization",
                model="facebook/bart-large-cnn",  # Sử dụng mô hình nhanh hơn
                device=0 if torch.cuda.is_available() else -1
            )
            print("Đã tải mô hình BART-CNN")
        except Exception as e:
            print(f"Không thể tải mô hình: {str(e)}")
            print("Sử dụng phương pháp trích xuất câu quan trọng")
            self.summarizer = None

    def process_single_text(self, text: str) -> str:
        """Xử lý một văn bản"""
        try:
            # Tiền xử lý
            text = self.preprocess_text(text)
            
            if self.summarizer is not None:
                # Tóm tắt với tham số tối ưu cho tốc độ
                summary = self.summarizer(
                    text,
                    max_length=130,      # Giảm độ dài tối đa
                    min_length=30,       # Giảm độ dài tối thiểu
                    length_penalty=1.0,   # Giảm penalty
                    num_beams=2,         # Giảm beam search
                    early_stopping=True
                )[0]['summary_text']
            else:
                # Sử dụng phương pháp trích xuất
                summary = extract_key_sentences(text, num_sentences=2)
            
            return self.postprocess_summary(summary)
            
        except Exception as e:
            print(f"Lỗi khi xử lý văn bản: {str(e)}")
            return extract_key_sentences(text, num_sentences=2)

    def preprocess_text(self, text: str) -> str:
        """Tiền xử lý văn bản trước khi tóm tắt"""
        # Làm sạch text
        text = clean_text(text)
        
        # Giới hạn độ dài văn bản
        words = text.split()
        if len(words) > 500:
            text = ' '.join(words[:500])
        
        return text

    def postprocess_summary(self, summary: str) -> str:
        """Hậu xử lý bản tóm tắt"""
        summary = clean_text(summary)
        if not summary.endswith(('.', '!', '?')):
            summary += '.'
        return summary

    def process_batch(self, texts: List[str], batch_size: int = 8) -> List[str]:
        """Xử lý và tóm tắt một batch các văn bản song song"""
        # Chia thành các batch nhỏ hơn
        batches = [texts[i:i + batch_size] for i in range(0, len(texts), batch_size)]
        summaries = []
        
        # Xử lý song song các batch
        with ThreadPoolExecutor(max_workers=4) as executor:
            for batch_summaries in executor.map(self.process_batch_internal, batches):
                summaries.extend(batch_summaries)
                print(f"Đã xử lý {len(summaries)}/{len(texts)} tin tức")
        
        return summaries

    def process_batch_internal(self, batch: List[str]) -> List[str]:
        """Xử lý một batch nội bộ"""
        return [self.process_single_text(text) for text in batch]

def summarize_news():
    """Hàm chính để tóm tắt tin tức"""
    print("Bắt đầu tóm tắt tin tức...")
    
    try:
        # Đọc dữ liệu
        with open("data/raw_news.json", "r", encoding="utf-8") as f:
            news_list = json.load(f)
        
        # Khởi tạo summarizer
        summarizer = NewsSummarizer()
        
        # Chuẩn bị danh sách văn bản
        texts = []
        for news in news_list:
            # Chỉ sử dụng tiêu đề và mô tả để tăng tốc
            text_parts = [news["title"]]
            if news.get("description"):
                text_parts.append(news["description"])
            text = " ".join(text_parts)
            texts.append(text)
        
        total = len(texts)
        print(f"Bắt đầu xử lý {total} tin tức...")
        
        # Xử lý theo batch
        summaries = summarizer.process_batch(texts)
        
        # Tạo kết quả
        processed_news = []
        for i, (news, summary) in enumerate(zip(news_list, summaries), 1):
            processed_news.append({
                "title": news["title"],
                "link": news["link"],
                "summary": summary,
                "description": news.get("description", ""),
                "category": news["category"],
                "source": news["source"],
                "timestamp": news["timestamp"]
            })
        
        # Lưu kết quả
        with open("data/processed_news.json", "w", encoding="utf-8") as f:
            json.dump(processed_news, f, ensure_ascii=False, indent=2)
        
        print("Đã hoàn thành tóm tắt tin tức!")
        
    except Exception as e:
        print(f"Lỗi trong quá trình xử lý: {str(e)}")
        raise

if __name__ == "__main__":
    summarize_news()
