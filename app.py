from flask import Flask, jsonify, request
import cloudscraper
from bs4 import BeautifulSoup

app = Flask(__name__)

# إعداد السكربت لتجاوز أي حماية
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'firefox',
        'platform': 'android',
        'desktop': False
    }
)

BASE_URL = "https://dilar.tube"

@app.route('/')
def home():
    return jsonify({
        "status": "success",
        "message": "Manga Black API (Dilar) is working successfully!"
    })

@app.route('/latest', methods=['GET'])
def get_latest():
    try:
        # جلب الصفحة الرئيسية للموقع أو صفحة أحدث الإصدارات
        response = scraper.get(BASE_URL, timeout=15)
        
        if response.status_code != 200:
            return jsonify({
                "success": False,
                "error": f"Failed to fetch website, status code: {response.status_code}"
            }), 500

        soup = BeautifulSoup(response.text, 'html.parser')
        
        manga_list = []
        # البحث عن عناصر المانجا والفصول الجديدة في موقع ديلار
        for item in soup.select('div.col, article, .manga-card, div.row.c-tabs-item__content'):
            title_tag = item.select_one('h3 a, h4 a, a.title, .post-title a')
            img_tag = item.select_one('img')
            
            if title_tag:
                title = title_tag.text.strip()
                link = title_tag.get('href', '')
                if link and not link.startswith('http'):
                    link = BASE_URL + link
                
                img_url = ''
                if img_tag:
                    img_url = img_tag.get('data-src') or img_tag.get('src') or ''
                
                manga_list.append({
                    'title': title,
                    'link': link,
                    'image': img_url
                })
                
        # إزالة العناصر المكررة إن وجدت
        seen = set()
        unique_manga = []
        for m in manga_list:
            if m['title'] not in seen:
                seen.add(m['title'])
                unique_manga.append(m)
                
        return jsonify({
            "success": True,
            "count": len(unique_manga),
            "data": unique_manga
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
