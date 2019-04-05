import requests
import paho.mqtt.client as mqtt
import json
from webexteamssdk import WebexTeamsAPI

api = WebexTeamsAPI(access_token="NTlmNWZmYTgtNWNmZC00Mjk1LTk1ZTYtZWI2Yzk3ZWU2NWE4YjI1Njc3OGItYTc5_PF84_a1254c6e-117d-49ff-9197-dd52b439f69c")


# client = mqtt.Client(client_id="JBS-PY-001", clean_session=True, userdata=None, protocol="MQTTv311", transport="tcp")
client = mqtt.Client(client_id="JBS-PY-001")


client.connect("192.168.1.244")



URL = "http://192.168.1.244:5001/location/simulation/lost"

response = requests.request('GET', URL)
person = response.json()
if person['is_lost'] == True:
        response_person = requests.request('GET', "http://192.168.1.246:8080/person/id/{}".format(person['id']))
        who = response_person.json()
        person["first_name"] = who['first_name']
        person["last_name"] = who['last_name']
        client.publish("person/status", json.dumps(person))
        link = "http://192.168.1.246:8080/person/{id}/map".format(id=who['id'])
        api.messages.create("Y2lzY29zcGFyazovL3VzL1JPT00vYzNhNjBlZjAtNTVmMS0xMWU5LWEyMmItZDkxYWYwODhkZGJh",
                        markdown="**Person is lost** \n\n {first_name} {last_name} is lost \n\n Check its location here {link}".format(
                                first_name=who['first_name'],
                                last_name=who['last_name'],
                                link=link))