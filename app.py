import os
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from dotenv import load_dotenv
import requests

load_dotenv()
app = Flask(__name__)
CORS(app)

AMAP_KEY = os.getenv("AMAP_KEY")
SEARCH_TEXT_URL = "https://restapi.amap.com/v3/place/text"
SEARCH_AROUND_URL = "https://restapi.amap.com/v3/place/around"

def get_metro_stations(city):
    """搜索城市里的地铁站"""
    params = {
        "key": AMAP_KEY,
        "keywords": "地铁站",
        "city": city,
        "offset": 20,
        "page": 1
    }
    r = requests.get(SEARCH_TEXT_URL, params=params, timeout=10)
    r.raise_for_status()
    pois = r.json().get("pois", [])
    return [{"name": poi["name"], "location": poi["location"]} for poi in pois]

def search_restaurants_nearby(location, radius=1000):
    """在某个坐标附近找餐馆"""
    params = {
        "key": AMAP_KEY,
        "location": location,
        "keywords": "餐馆",
        "radius": radius,
        "offset": 50,
        "page": 1,
        "extensions": "all"
    }
    r = requests.get(SEARCH_AROUND_URL, params=params, timeout=10)
    r.raise_for_status()
    pois = r.json().get("pois", [])
    results = []
    for poi in pois:
        rating = poi.get("biz_ext", {}).get("rating", "0")
        results.append({
            "名称": poi.get("name"),
            "地址": poi.get("address"),
            "类型": poi.get("type"),
            "评分": rating,
            "距离": poi.get("distance"),
            "位置": poi.get("location")
        })
    return results

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def search():
    data = request.json
    city = data.get('city', '西安')

    # 获取地铁站
    stations = get_metro_stations(city)

    # 获取所有地铁站附近的餐馆
    all_restaurants = []
    for station in stations:
        restaurants = search_restaurants_nearby(station["location"])
        all_restaurants.extend(restaurants)

    # 按评分排序（降序）
    all_restaurants.sort(key=lambda x: float(x["评分"]) if x["评分"] else 0, reverse=True)

    return jsonify({
        "success": True,
        "restaurants": all_restaurants,
        "total": len(all_restaurants)
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)