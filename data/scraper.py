import requests
from bs4 import BeautifulSoup
import json

def scrape_vnexpress():
    url = "https://vnexpress.net/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    news_list = []
    for h3 in soup.find_all("h3", class_="title-news"):
        title = h3.text.strip()
        link = h3.a["href"] if h3.a else "#"
        news_list.append({"title": title, "link": link})

    return news_list

if __name__ == "__main__":
    news = scrape_vnexpress()
    with open("data/raw_news.json", "w", encoding="utf-8") as f:
        json.dump(news, f, ensure_ascii=False, indent=4)
    print("Đã lưu dữ liệu tin tức!")
