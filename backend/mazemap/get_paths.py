import requests
import json
import pprint
import numpy as np

pp = pprint.PrettyPrinter(indent=4)

MAZEMAP_BASE_URL='https://api.mazemap.com/'
ROUTE_URL='routing/path/?'

import geopy.distance

coords_canteen = (10.626261489752778, 59.91008822603314)
coords_quiet_room = (10.62432177904725, 59.90966314352917)
coords_reception = (10.625762180826769, 59.90986003189486)

# coords_lost = (10.625762180826769, 59.90986003189486)
coords_lost = coords_reception

def is_lost(distances):
    closest_point = 100
    for distance in distances:
        if closest_point > distance:
            closest_point = distance
    if closest_point > 5:
        return True
    else:
        return False


def get_distances(points):
    distances = []
    for point in points:
        distances.append(geopy.distance.distance(
            coords_lost,
            point
        ).m)
    return distances

def get_points(data):
    points = []
    for feature in data['path']['features']:
        feature_coordinates = feature['geometry']['coordinates']
        distance_lat = feature_coordinates[1][0] - feature_coordinates[0][0]
        distance_lon = feature_coordinates[1][1] - feature_coordinates[0][1]
        diff_lat = distance_lat / 3
        diff_lon = distance_lon / 3
        i = 0
        points.append(feature_coordinates[0])
        new_lat = feature_coordinates[0][0]
        new_lon = feature_coordinates[0][1]
        points.append(feature_coordinates[0])
        while i < 3:
            new_lat = new_lat + diff_lat
            new_lon = new_lon + diff_lon
            points.append([new_lat, new_lon])
            i = i + 1
    return points

def route_path(srid, hc, sourcelat, sourcelon, targetlat, targetlon, sourcez, targetz, lang, distanceunitstype):
    URL = MAZEMAP_BASE_URL + ROUTE_URL
    params= {
        "srid": srid,
        "hc": hc,
        "sourcelat": sourcelat,
        "sourcelon": sourcelon,
        "targetlat": targetlat,
        "targetlon": targetlon,
        "sourcez": sourcez,
        "targetz": targetz,
        "lang": lang,
        "distanceunitstype": distanceunitstype
    }
    response = requests.request('GET', URL, params=params)
    json_data = response.json()
    return json_data
    # segments(json_data)
    # user_eta = json_data['pathMetrics']['durationWalkingMinutes']
    # headers = {'Content-Type': 'application/json'}
    # info = {'eta': user_eta}
    # requests.request('POST', 'http://127.0.0.1:3000/eta', data = json.dumps(info), headers=headers)

# route_path(srid=4326, hc=False, sourcelat=59.90996761463981, sourcelon=10.625416100871462,
# targetlat=59.910000116669536, targetlon=10.625750437404122, sourcez=1, 
# targetz=1, lang='en', distanceunitstype='metric')

json_data = route_path(srid=4326, 
hc=False, 
sourcelat=59.90977037559057, 
sourcelon=10.624818365837882, 
targetlat=59.910000116669536, 
targetlon=10.625750437404122, 
sourcez=1, 
targetz=1, 
lang='en', 
distanceunitstype='metric')

points = get_points(json_data)
distances = get_distances(points)
lost = is_lost(distances)
print(lost)