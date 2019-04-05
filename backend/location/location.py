from flask import Flask, request, abort,jsonify
import json
import sqlite3
import requests
# conn = sqlite3.connect('../db/example.db')


# coords_canteen = (10.626261489752778, 59.91008822603314)
# coords_quiet_room = (10.62432177904725, 59.90966314352917)
# coords_reception = (10.625762180826769, 59.90986003189486)

import geopy.distance

MAZEMAP_BASE_URL='https://api.mazemap.com/'
ROUTE_URL='routing/path/?'

def is_lost(distances):
    closest_point = 100
    for distance in distances:
        if closest_point > distance:
            closest_point = distance
            # print('CLOSEST POINT', closest_point, distance)
    # print("THE POINT IS: ", closest_point) 
    if closest_point > 10:
        # print(closest_point)
        return True
    else:
        return False


def get_distances(points, location_lat, location_lon):
    distances = []
    for point in points:
        distances.append(geopy.distance.distance(
            (location_lon, location_lat),
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

app = Flask(__name__)

@app.route('/new-person', methods=['POST'])
def webhook():
    with sqlite3.connect("../db/hackathon.db") as conn:
        json_data = request.json
        person = json_data['person']

        # Insert a row of data
        c = conn.cursor()
        c.execute("INSERT INTO person VALUES ({0}, {1}, {2}, {3}, {4}, '{5}')".format(person['id'],
        59.90983125346216, 10.625703081412468, json_data['meeting_lat'], json_data['meeting_lng'], json_data['ip']))

        # Save (commit) the changes
        conn.commit()

        # We can also close the connection if we are done with it.
        # Just be sure any changes have been committed or they will be lost.
        return '', 200


@app.route('/location/users', methods=['GET'])
def get_users():
    with sqlite3.connect("../db/hackathon.db") as conn:
        # Insert a row of data
        c = conn.cursor()
        c.execute("SELECT userid, src_lat, src_long, dst_lat, dst_long, ip FROM person")
        people = c.fetchall()
        people_json = []
        for person in people:
            response_location = requests.request('GET', 'https://staging-cloudpositioning.mazemap.com/position?ipv4={0}'.format(person[5]))
            current_location = response_location.json()
            is_lost = is_person_lost(person[1], person[2], person[3], person[4], current_location['latitude'], current_location['longitude'])
            people_json.append({
                "id": person[0],
                "src_lat": person[1],
                "src_lon": person[2],
                "dst_lat": person[3],
                "dst_lon": person[4],
                "ip": person[5],
                "is_lost": is_lost
            })
        return jsonify(people_json)


@app.route('/location/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    with sqlite3.connect("../db/hackathon.db") as conn:
        # Insert a row of data
        c = conn.cursor()
        c.execute("SELECT userid, src_lat, src_long, dst_lat, dst_long, ip FROM person WHERE userid={0}".format(user_id))
        person = c.fetchone()
        response_location = requests.request('GET', 'https://staging-cloudpositioning.mazemap.com/position?ipv4={0}'.format(person[5]))
        current_location = response_location.json()
        is_lost = is_person_lost(person[1], person[2], person[3], person[4], current_location['latitude'], current_location['longitude'])
        people_json = {
            "id": person[0],
            "src_lat": person[1],
            "src_lon": person[2],
            "dst_lat": person[3],
            "dst_lon": person[4],
            "ip": person[5],
            "is_lost": is_lost
        }
        return jsonify(people_json)

@app.route('/location/simulation/lost', methods=['GET'])
def lost_user():
    with sqlite3.connect("../db/hackathon.db") as conn:
        # Insert a row of data
        c = conn.cursor()
        c.execute("SELECT userid, src_lat, src_long, dst_lat, dst_long, ip FROM person WHERE userid={0}".format(4))
        person = c.fetchone()
        is_lost = is_person_lost(person[1], person[2], person[3], person[4], 59.91008822603314, 10.626261489752778)
        people_json = {
            "id": person[0],
            "src_lat": person[1],
            "src_lon": person[2],
            "dst_lat": person[3],
            "dst_lon": person[4],
            "ip": person[5],
            "is_lost": is_lost,
            "curr_lat": 59.91008822603314,
            "curr_lon": 10.626261489752778 
        }
        return jsonify(people_json)

@app.route('/location/simulation/not_lost', methods=['GET'])
def not_lost_user():
    with sqlite3.connect("../db/hackathon.db") as conn:
        # Insert a row of data
        c = conn.cursor()
        c.execute("SELECT userid, src_lat, src_long, dst_lat, dst_long, ip FROM person WHERE userid={0}".format(5))
        person = c.fetchone()
        is_lost = is_person_lost(person[1], person[2], person[3], person[4], 59.90996556795713, 10.625879151085266)
        people_json = {
            "id": person[0],
            "src_lat": person[1],
            "src_lon": person[2],
            "dst_lat": person[3],
            "dst_lon": person[4],
            "ip": person[5],
            "is_lost": is_lost,
            "curr_lat": 59.90996556795713,
            "curr_lon": 10.625879151085266 
        }
        return jsonify(people_json)


if __name__ == '__main__':
    app.run(host= '0.0.0.0', port='5001', debug=True)