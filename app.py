from flask import Flask, jsonify, request
import cloudscraper
from bs4 import BeautifulSoup

app = Flask(__name__)
scraper = cloudscraper.create_scraper()
BASE_URL = "https://manga3asq.com"

@app.route('/')
def home():
    return jsonify({
        "status": "success",
        "message": "Manga Black API is working successfully!"
    })

@app.route('/latest', methods=['GET'])
def get_latest():
    try:
        page = request.args.get('page', 1)
        url = f"{BASE_URL}/page/{page}/" if int(page) > 1 else BASE_URL
        
        response = scraper.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        manga_list = []
        for item in soup.select('div.page-item-detail, div.manga-item'):
            title_tag = item.select_one('h3 a, h4 a, .post-title a')
            img_tag = item.select_one('img')
            
            if title_tag:
                title = title_tag.text.strip()
                link = title_tag.get('href', '')
                
                img_url = ''
                if img_tag:
                    img_url = img_tag.get('src') or img_tag.get('data-src') or ''
                
                manga_list.append({
                    'title': title,
                    'link': link,
                    'image': img_url
                })
                
        return jsonify({
            "success": True,
            "count": len(manga_list),
            "data": manga_list
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
