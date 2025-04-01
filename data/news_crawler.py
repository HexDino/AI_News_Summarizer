from bs4 import BeautifulSoup
import requests
import json
from typing import List, Dict
from datetime import datetime
from abc import ABC, abstractmethod
import re
from urllib.parse import urljoin
from sklearn.feature_extraction.text import TfidfVectorizer
from concurrent.futures import ThreadPoolExecutor

class NewsCrawler(ABC):
    """Abstract base class cho các crawler của từng trang báo"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    @abstractmethod
    def get_category_urls(self) -> Dict[str, str]:
        """Trả về dictionary của các category và URL của chúng"""
        pass

    @abstractmethod
    def extract_news(self, html: str, category: str) -> List[Dict]:
        """Trích xuất tin tức từ HTML của một trang"""
        pass

    def crawl(self) -> List[Dict]:
        """Crawl tin tức từ tất cả các category"""
        all_news = []
        for category, url in self.get_category_urls().items():
            try:
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                news_items = self.extract_news(response.text, category)
                all_news.extend(news_items)
                print(f"Đã crawl {len(news_items)} tin từ category {category}")
            except Exception as e:
                print(f"Lỗi khi crawl category {category}: {str(e)}")
        return all_news

class VnExpressCrawler(NewsCrawler):
    def get_category_urls(self) -> Dict[str, str]:
        return {
            "thời sự": "https://vnexpress.net/thoi-su",
            "thế giới": "https://vnexpress.net/the-gioi",
            "kinh doanh": "https://vnexpress.net/kinh-doanh",
            "giải trí": "https://vnexpress.net/giai-tri",
            "thể thao": "https://vnexpress.net/the-thao",
            "khoa học": "https://vnexpress.net/khoa-hoc",
            "giáo dục": "https://vnexpress.net/giao-duc"
        }

    def extract_news(self, html: str, category: str) -> List[Dict]:
        soup = BeautifulSoup(html, 'html.parser')
        news_items = []
        
        for article in soup.find_all('article', class_='item-news'):
            try:
                title_tag = article.find('h3', class_='title-news')
                if not title_tag or not title_tag.a:
                    continue
                    
                title = title_tag.a.text.strip()
                link = title_tag.a['href']
                description = ""
                
                desc_tag = article.find('p', class_='description')
                if desc_tag:
                    description = desc_tag.text.strip()

                words = description.split()
                if len(words) > 500:
                    description = ' '.join(words[:500])

                news_items.append({
                    "title": title,
                    "link": link,
                    "description": description,
                    "category": category,
                    "source": "VnExpress",
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                print(f"Lỗi khi xử lý một tin VnExpress: {str(e)}")
                
        return news_items

class TuoiTreCrawler(NewsCrawler):
    def get_category_urls(self) -> Dict[str, str]:
        return {
            "thời sự": "https://tuoitre.vn/thoi-su.htm",
            "thế giới": "https://tuoitre.vn/the-gioi.htm",
            "kinh doanh": "https://tuoitre.vn/kinh-doanh.htm",
            "giải trí": "https://tuoitre.vn/giai-tri.htm",
            "thể thao": "https://tuoitre.vn/the-thao.htm",
            "khoa học": "https://tuoitre.vn/khoa-hoc.htm",
            "giáo dục": "https://tuoitre.vn/giao-duc.htm"
        }

    def extract_news(self, html: str, category: str) -> List[Dict]:
        soup = BeautifulSoup(html, 'html.parser')
        news_items = []
        
        for article in soup.find_all('div', class_='news-item'):
            try:
                title_tag = article.find('h3', class_='title-news')
                if not title_tag or not title_tag.a:
                    continue
                    
                title = title_tag.a.text.strip()
                link = urljoin("https://tuoitre.vn", title_tag.a['href'])
                description = ""
                
                desc_tag = article.find('div', class_='description')
                if desc_tag:
                    description = desc_tag.text.strip()

                words = description.split()
                if len(words) > 500:
                    description = ' '.join(words[:500])

                news_items.append({
                    "title": title,
                    "link": link,
                    "description": description,
                    "category": category,
                    "source": "Tuổi Trẻ",
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                print(f"Lỗi khi xử lý một tin Tuổi Trẻ: {str(e)}")
                
        return news_items

class ThanhNienCrawler(NewsCrawler):
    def get_category_urls(self) -> Dict[str, str]:
        return {
            "thời sự": "https://thanhnien.vn/thoi-su/",
            "thế giới": "https://thanhnien.vn/the-gioi/",
            "kinh doanh": "https://thanhnien.vn/tai-chinh-kinh-doanh/",
            "giải trí": "https://thanhnien.vn/giai-tri/",
            "thể thao": "https://thanhnien.vn/the-thao/",
            "khoa học": "https://thanhnien.vn/khoa-hoc-cong-nghe/",
            "giáo dục": "https://thanhnien.vn/giao-duc/"
        }

    def extract_news(self, html: str, category: str) -> List[Dict]:
        soup = BeautifulSoup(html, 'html.parser')
        news_items = []
        
        for article in soup.find_all('article', class_='story'):
            try:
                title_tag = article.find('h2', class_='story__title')
                if not title_tag or not title_tag.a:
                    continue
                    
                title = title_tag.a.text.strip()
                link = urljoin("https://thanhnien.vn", title_tag.a['href'])
                description = ""
                
                desc_tag = article.find('div', class_='story__description')
                if desc_tag:
                    description = desc_tag.text.strip()

                words = description.split()
                if len(words) > 500:
                    description = ' '.join(words[:500])

                news_items.append({
                    "title": title,
                    "link": link,
                    "description": description,
                    "category": category,
                    "source": "Thanh Niên",
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                print(f"Lỗi khi xử lý một tin Thanh Niên: {str(e)}")
                
        return news_items

class DanTriCrawler(NewsCrawler):
    def get_category_urls(self) -> Dict[str, str]:
        return {
            "thời sự": "https://dantri.com.vn/xa-hoi.htm",
            "thế giới": "https://dantri.com.vn/the-gioi.htm",
            "kinh doanh": "https://dantri.com.vn/kinh-doanh.htm",
            "giải trí": "https://dantri.com.vn/giai-tri.htm",
            "thể thao": "https://dantri.com.vn/the-thao.htm",
            "khoa học": "https://dantri.com.vn/khoa-hoc-cong-nghe.htm",
            "giáo dục": "https://dantri.com.vn/giao-duc-huong-nghiep.htm"
        }

    def extract_news(self, html: str, category: str) -> List[Dict]:
        soup = BeautifulSoup(html, 'html.parser')
        news_items = []
        
        for article in soup.find_all('article', class_='article-item'):
            try:
                title_tag = article.find('h3', class_='article-title')
                if not title_tag or not title_tag.a:
                    continue
                    
                title = title_tag.a.text.strip()
                link = urljoin("https://dantri.com.vn", title_tag.a['href'])
                description = ""
                
                desc_tag = article.find('div', class_='article-excerpt')
                if desc_tag:
                    description = desc_tag.text.strip()

                words = description.split()
                if len(words) > 500:
                    description = ' '.join(words[:500])

                news_items.append({
                    "title": title,
                    "link": link,
                    "description": description,
                    "category": category,
                    "source": "Dân Trí",
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                print(f"Lỗi khi xử lý một tin Dân Trí: {str(e)}")
                
        return news_items

class ZingNewsCrawler(NewsCrawler):
    def get_category_urls(self) -> Dict[str, str]:
        return {
            "thời sự": "https://zingnews.vn/thoi-su.html",
            "thế giới": "https://zingnews.vn/the-gioi.html",
            "kinh doanh": "https://zingnews.vn/kinh-doanh-tai-chinh.html",
            "giải trí": "https://zingnews.vn/giai-tri.html",
            "thể thao": "https://zingnews.vn/the-thao.html",
            "khoa học": "https://zingnews.vn/khoa-hoc.html",
            "giáo dục": "https://zingnews.vn/giao-duc.html"
        }

    def extract_news(self, html: str, category: str) -> List[Dict]:
        soup = BeautifulSoup(html, 'html.parser')
        news_items = []
        
        for article in soup.find_all('article', class_='article-item'):
            try:
                title_tag = article.find('header', class_='article-header')
                if not title_tag or not title_tag.p or not title_tag.p.a:
                    continue
                    
                title = title_tag.p.a.text.strip()
                link = urljoin("https://zingnews.vn", title_tag.p.a['href'])
                description = ""
                
                desc_tag = article.find('p', class_='article-summary')
                if desc_tag:
                    description = desc_tag.text.strip()

                words = description.split()
                if len(words) > 500:
                    description = ' '.join(words[:500])

                news_items.append({
                    "title": title,
                    "link": link,
                    "description": description,
                    "category": category,
                    "source": "Zing News",
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                print(f"Lỗi khi xử lý một tin Zing News: {str(e)}")
                
        return news_items

class VTVNewsCrawler(NewsCrawler):
    def get_category_urls(self) -> Dict[str, str]:
        return {
            "thời sự": "https://vtv.vn/thoi-su.htm",
            "thế giới": "https://vtv.vn/the-gioi.htm",
            "kinh doanh": "https://vtv.vn/kinh-te.htm",
            "giải trí": "https://vtv.vn/van-hoa-giai-tri.htm",
            "thể thao": "https://vtv.vn/the-thao.htm",
            "khoa học": "https://vtv.vn/khoa-hoc-cong-nghe.htm",
            "giáo dục": "https://vtv.vn/giao-duc.htm"
        }

    def extract_news(self, html: str, category: str) -> List[Dict]:
        soup = BeautifulSoup(html, 'html.parser')
        news_items = []
        
        for article in soup.find_all('div', class_='item-news'):
            try:
                title_tag = article.find('h3', class_='title')
                if not title_tag or not title_tag.a:
                    continue
                    
                title = title_tag.a.text.strip()
                link = urljoin("https://vtv.vn", title_tag.a['href'])
                description = ""
                
                desc_tag = article.find('div', class_='sapo')
                if desc_tag:
                    description = desc_tag.text.strip()

                words = description.split()
                if len(words) > 500:
                    description = ' '.join(words[:500])

                news_items.append({
                    "title": title,
                    "link": link,
                    "description": description,
                    "category": category,
                    "source": "VTV News",
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                print(f"Lỗi khi xử lý một tin VTV News: {str(e)}")
                
        return news_items

def crawl_all_news():
    """Crawl tin tức từ tất cả các nguồn"""
    crawlers = [
        VnExpressCrawler(),
        TuoiTreCrawler(),
        ThanhNienCrawler(),
        DanTriCrawler(),
        ZingNewsCrawler(),
        VTVNewsCrawler()
    ]
    
    all_news = []
    for crawler in crawlers:
        try:
            news = crawler.crawl()
            all_news.extend(news)
        except Exception as e:
            print(f"Lỗi khi crawl từ {crawler.__class__.__name__}: {str(e)}")
    
    # Lưu tin tức theo từng category
    news_by_category = {}
    for item in all_news:
        category = item["category"]
        if category not in news_by_category:
            news_by_category[category] = []
        news_by_category[category].append(item)
    
    # Lưu tin tức vào các file riêng biệt theo category
    for category, news in news_by_category.items():
        filename = f"data/raw_news_{category.replace(' ', '_')}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(news, f, ensure_ascii=False, indent=2)
    
    # Lưu tất cả tin tức vào một file
    with open("data/raw_news.json", "w", encoding="utf-8") as f:
        json.dump(all_news, f, ensure_ascii=False, indent=2)
    
    print(f"Đã crawl tổng cộng {len(all_news)} tin tức từ {len(crawlers)} nguồn")
    print(f"Phân loại theo category: {', '.join(news_by_category.keys())}")

if __name__ == "__main__":
    crawl_all_news() 