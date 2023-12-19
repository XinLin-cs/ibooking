from math import radians, sin, cos, sqrt, atan2
import json

def calculate_distance(lat1, lon1, lat2, lon2):
    # 将经纬度从度数转换为弧度
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Haversine公式计算两点间距离
    d_lat = lat2 - lat1
    d_lon = lon2 - lon1
    a = sin(d_lat/2)**2 + cos(lat1) * cos(lat2) * sin(d_lon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = 6371 * c  # 地球平均半径为6371km

    return distance

def getFile(path):
    with open(path, "r") as f:
        js = json.load(f)
        return js