import os
import requests
from dotenv import load_dotenv

load_dotenv()
AMAP_KEY = os.getenv("AMAP_KEY")
SEARCH_TEXT_URL = "https://restapi.amap.com/v3/place/text"
SEARCH_AROUND_URL = "https://restapi.amap.com/v3/place/around"

def get_metro_stations(city="西安"):
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
        "location": location,  # 格式 "经度,纬度"
        "keywords": "餐馆",
        "radius": radius,
        "offset": 10,
        "page": 1,
        "extensions": "all"  # 确保能拿到评分和距离
    }
    r = requests.get(SEARCH_AROUND_URL, params=params, timeout=10)
    r.raise_for_status()
    pois = r.json().get("pois", [])
    results = []
    for poi in pois:
        results.append({
            "名称": poi.get("name"),
            "地址": poi.get("address"),
            "类型": poi.get("type"),
            "评分": poi.get("biz_ext", {}).get("rating"),
            "距离(米)": poi.get("distance")
        })
    return results

if __name__ == "__main__":
    # 第一步：获取西安所有地铁站
    stations = get_metro_stations("西安")
    print(f"找到 {len(stations)} 个地铁站")

    # 第二步：取前 3 个地铁站做测试
    for station in stations[:3]:
        print(f"\n📍 {station['name']} 附近餐馆：")
        restaurants = search_restaurants_nearby(station["location"])
        for r in restaurants:
            print(r)
