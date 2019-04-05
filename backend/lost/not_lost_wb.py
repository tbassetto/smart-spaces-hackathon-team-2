import requests
import paho.mqtt.client as mqtt
import json

# client = mqtt.Client(client_id="JBS-PY-001", clean_session=True, userdata=None, protocol="MQTTv311", transport="tcp")
client = mqtt.Client(client_id="JBS-PY-001")


client.connect("192.168.1.244")



URL = "http://192.168.1.244:5001/location/simulation/not_lost"

response = requests.request('GET', URL)
person = response.json()
person['eta'] = 2
client.publish("person/webexboard", json.dumps(person))
