import requests
import paho.mqtt.client as mqtt
import json

# client = mqtt.Client(client_id="JBS-PY-001", clean_session=True, userdata=None, protocol="MQTTv311", transport="tcp")
client = mqtt.Client(client_id="JBS-PY-001")


client.connect("192.168.1.244")



URL = "http://192.168.1.244:5001/location/simulation/lost"

response = requests.request('GET', URL)
person = response.json()
if person['is_lost'] == True:
        client.publish("person/webexboard", json.dumps(person))
