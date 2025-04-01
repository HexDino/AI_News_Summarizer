from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import json
from datetime import datetime
import os
from glob import glob

app = FastAPI(
    title="News Summarizer API",
    description="API để lấy tin tức đã được tóm tắt bằng AI từ nhiều nguồn",
    version="1.0.0"
)

# Cho phép CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class NewsItem(BaseModel):
    title: str
    link: str
    summary: str
    description: Optional[str] = None
    category: str
    source: str
    timestamp: str

class NewsResponse(BaseModel):
    status: str
    total: int
    last_updated: str
    categories: List[str]
    sources: List[str]
    news: List[NewsItem]

def get_available_categories() -> List[str]:
    """Lấy danh sách các category có sẵn"""
    pattern = os.path.join("data", "raw_news_*.json")
    files = glob(pattern)
    categories = []
    for file in files:
        category = os.path.basename(file).replace("raw_news_", "").replace(".json", "").replace("_", " ")
        categories.append(category)
    return sorted(categories)

def get_available_sources() -> List[str]:
    """Lấy danh sách các nguồn tin có sẵn"""
    try:
        with open("data/raw_news.json", "r", encoding="utf-8") as f:
            news_list = json.load(f)
        return sorted(list(set(item["source"] for item in news_list)))
    except:
        return []

@app.get("/news", response_model=NewsResponse)
def get_news(
    category: Optional[str] = Query(None, description="Lọc theo category"),
    source: Optional[str] = Query(None, description="Lọc theo nguồn tin"),
    search: Optional[str] = Query(None, description="Tìm kiếm trong tiêu đề và mô tả")
):
    try:
        # Đọc tin tức từ file phù hợp
        if category:
            filename = f"data/raw_news_{category.replace(' ', '_')}.json"
            if not os.path.exists(filename):
                raise HTTPException(status_code=404, detail=f"Không tìm thấy category: {category}")
            with open(filename, "r", encoding="utf-8") as f:
                news_list = json.load(f)
        else:
            with open("data/processed_news.json", "r", encoding="utf-8") as f:
                news_list = json.load(f)
        
        # Lọc theo nguồn nếu có
        if source:
            news_list = [news for news in news_list if news["source"].lower() == source.lower()]
            
        # Tìm kiếm nếu có
        if search:
            search = search.lower()
            news_list = [
                news for news in news_list 
                if search in news["title"].lower() 
                or (news.get("description", "") and search in news["description"].lower())
            ]
            
        # Thêm timestamp nếu chưa có
        for news in news_list:
            if "timestamp" not in news:
                news["timestamp"] = datetime.now().isoformat()
            
        return {
            "status": "success",
            "total": len(news_list),
            "last_updated": datetime.now().isoformat(),
            "categories": get_available_categories(),
            "sources": get_available_sources(),
            "news": news_list
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/categories")
def get_categories():
    """Lấy danh sách tất cả các category có sẵn"""
    return {"categories": get_available_categories()}

@app.get("/sources")
def get_sources():
    """Lấy danh sách tất cả các nguồn tin có sẵn"""
    return {"sources": get_available_sources()}

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
