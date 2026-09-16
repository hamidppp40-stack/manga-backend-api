from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# استخدام الـ API المباشر الذي أعطيتني إياه
MANGA_API_URL = "https://api.coffeemanga.shop"

@app.route('/')
def home():
    return jsonify({
        "status": "success",
        "message": "Manga Black API (Connected) is working successfully!"
    })

@app.route('/latest', methods=['GET'])
def get_latest():
    try:
        # جلب البيانات مباشرة من الـ API الحقيقي
        response = requests.get(MANGA_API_URL, timeout=15)
        
        if response.status_code != 200:
            return jsonify({
                "success": False,
                "error": f"Failed to fetch from API, status code: {response.status_code}"
            }), 500

        # محاولة قراءة البيانات كـ JSON
        data = response.json()
        
        return jsonify({
            "success": True,
            "data": data
        })
        
    except Exception as e:
        # إذا كان الـ API يرجع HTML أو خطأ، نعيد رسالة واضحة
        return jsonify({
            "success": False,
            "error": str(e),
            "fallback_api": "https://api.mangapdf.org"
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
