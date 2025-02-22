import googlemaps
import math

gmaps = googlemaps.Client(key='AIzaSyCiI_vKg-YEu3P7yQTDqPg9AdIBmLZJmPk')

# ============================ config ====================================
center = '701台南市東區東寧路120巷20號'
open_or_not = True
distance = 20000
rating = 4
eat = '牛肉湯'
# ========================================================================


def calculate_bearing(lat1, lon1, lat2, lon2):
    """
    Calculate the bearing (direction) from point A to point B.
    Inputs are the latitude and longitude of both points in decimal degrees.
    Returns the bearing in degrees (clockwise from north).
    """
    # Convert decimal degrees to radians
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    # Calculate differences in longitudes and latitudes
    delta_lon = lon2 - lon1

    # Calculate bearing
    y = math.sin(delta_lon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(delta_lon)
    bearing_rad = math.atan2(y, x)

    # Convert bearing from radians to degrees
    bearing_deg = math.degrees(bearing_rad)

    # Normalize to a compass bearing (0 to 360 degrees)
    bearing_deg = (bearing_deg + 360) % 360

    return bearing_deg


def get_direction(bearing):
    directions = ["北", "東北", "東", "東南", "南", "西南", "西", "西北"]
    index = round(bearing / 45) % 8
    return directions[index]


def calculate_distance(lat1, lon1, lat2, lon2, unit='km'):
    # approximate radius of earth in km
    R = 6371.0 if unit == 'km' else 3956.0

    # convert degrees to radians
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    # calculate change in coordinates
    dlon = lon2 - lon1
    dlat = lat2 - lat1

    # apply Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # calculate distance
    distance = R * c

    return distance


# 利用Geocode函數進行定位
geocode_result = gmaps.geocode(center)[0]
location = geocode_result['geometry']['location']
lat1, lng1 = location['lat'], location['lng']

# (keyword參數="輸入你想查詢的物件",radius="公尺單位")
places_result = gmaps.places_nearby(location, keyword=eat, radius=distance)

target = []
for place in places_result['results']:
    if place['business_status'] == 'OPERATIONAL':
        if place['rating'] >= rating:
            target.append(place)

for place in target:
    try:
        price = place['price_level']
    except:
        price = None

    try:
        lat2, lng2 = place['geometry']['location']['lat'], place['geometry']['location']['lng']
        direction = get_direction(calculate_bearing(lat1, lng1, lat2, lng2))
    except:
        direction = None
        lat2, lng2 = None, None

    try:
        open_or_not = place['opening_hours']['open_now']
    except:
        open_or_not = None

    try:
        length = calculate_distance(lat1, lng1, lat2, lng2)
    except:
        length = None

    print('店名：{}'.format(place['name']))
    print('Google評分：{},   有開嗎：{},   方位：{}邊 {}km \n'.format(place['rating'], open_or_not, direction, length))


