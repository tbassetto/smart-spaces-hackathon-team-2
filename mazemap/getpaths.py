import requests
import json
import geopy.distance

MAZEMAP_BASE_URL='https://api.mazemap.com/'
ROUTE_URL='routing/path/?'

def is_lost(distances):
    closest_point = 100
    for distance in distances:
        if closest_point > distance:
            closest_point = distance
    if closest_point > 5:
        return True
    else:
        return False


def get_distances(points, location_lat, location_lon):
    distances = []
    for point in points:
        distances.append(geopy.distance.distance(
            (location_lat, location_lon),
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

def is_person_lost(src_lat, src_lon, dst_lat, dst_lon, location_lat, location_lon):
    json_data = route_path(srid=4326, 
    hc=False, 
    sourcelat=src_lat, 
    sourcelon=src_lon,
    targetlat=dst_lat,
    targetlon=dst_lon,
    sourcez=1, 
    targetz=1, 
    lang='en', 
    distanceunitstype='metric')

    points = get_points(json_data)
    distances = get_distances(points, location_lat, location_lon)
    lost = is_lost(distances)
    return lost