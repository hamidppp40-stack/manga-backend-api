from flask import Flask, request, jsonify
import cloudscraper
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

scraper = cloudscraper.create_scraper()
BASE_URL = "https://manga3asq.com"

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "Server is running successfully!"})

@app.route('/manga-list', methods=['GET'])
def get_manga_list():
    try:
        response = scraper.get(f"{BASE_URL}/manga/?list", headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        manga_list = []
        for a_tag in soup.find_all('a'):
            href = a_tag.get('href', '')
            img_tag = a_tag.find('img')
            
            if '/manga/' in href and href != f"{BASE_URL}/manga/":
                title = a_tag.text.strip()
                cover = ""
                if img_tag:
                    title = img_tag.get('alt') or img_tag.get('title') or title
                    cover = img_tag.get('src') or img_tag.get('data-src') or ""
                
                if title and len(title) > 1:
                    manga_list.append({
                        "title": title,
                        "url": href,
                        "cover": cover
                    })
                
        unique_manga = list({v['url']: v for v in manga_list}.values())
        return jsonify({"success": True, "count": len(unique_manga), "data": unique_manga})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/get-chapters', methods=['GET'])
def get_chapters():
    manga_url = request.args.get('url')
    if not manga_url:
        return jsonify({"error": "Missing url"}), 400
        
    try:
        response = scraper.get(manga_url, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        chapters = []
        for ch in soup.find_all('a'):
            href = ch.get('href', '')
            text = ch.text.strip()
            if '/chapter/' in href or 'manga3asq.com/' in href:
                if 'فصل' in text or 'Chapter' in text or 'ch-' in href:
                    chapters.append({
                        "chapter_title": text if text else "فصل",
                        "url": href
                    })
            
        unique_chapters = list({v['url']: v for v in chapters}.values())
        return jsonify({"success": True, "chapters": unique_chapters})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/get-pages', methods=['GET'])
def get_pages():
    chapter_url = request.args.get('url')
    if not chapter_url:
        return jsonify({"error": "Missing url"}), 400
        
    try:
        response = scraper.get(chapter_url, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        images = []
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if src and ('uploads' in src or 'wp-content' in src):
                images.append(src.strip())
                
        return jsonify({"success": True, "pages": images})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
