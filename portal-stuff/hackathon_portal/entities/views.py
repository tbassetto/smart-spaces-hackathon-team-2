from django.shortcuts import render

from django.http import HttpResponse, JsonResponse
from django.views import View
from django.core import serializers
from .models import Meeting, Person, PersonIpLink
from django.conf import settings
from webexteamssdk import WebexTeamsAPI

import requests
import json
import random
import paho.mqtt.client as mqtt


# Create your views here.
class MeetingView(View):
    def get(self, request, meeting_id):
        meeting = Meeting.objects.filter(meeting_id=meeting_id).first()

        if meeting is None:
            return HttpResponse("Sorry. No meeting with this id. You sure you belong here?")

        ctx = {
            "meeting": meeting,
        }
        return render(request, "entities/meeting.html", ctx)

class NavigationView(View):
    def get(self, request, meeting_id, person_id):
        meeting = Meeting.objects.filter(meeting_id=meeting_id).first()
        person = Person.objects.filter(id=person_id).first()

        if not all([meeting, person]):
            return HttpResponse("New server. Who dis?")

        ctx = {
            "meeting": meeting,
            "person": person
        }
        api = WebexTeamsAPI(access_token=settings.WEBEX_TEAMS_TOKEN)
        api.messages.create(toPersonEmail="mneiding@cisco.com", markdown="Your meeting participant {} arrived and is on the way".format(person.first_name))

        return render(request, "entities/navigate.html", ctx)

class MeetingMapView(View):
    def get(self, request, meeting_id):
        meeting = Meeting.objects.filter(meeting_id=meeting_id).first()

        if meeting is None:
            return HttpResponse("New meeting. Who dis?")

        ctx = {
            "meeting": meeting,
            "persons": [str(p.id) for p in meeting.participants.all()],
            "type": "overview",
        }

        return render(request, "entities/meeting_map.html", ctx)
class MapLocationView(View):
    def get(self, request, person_id):
        return HttpResponse("Display map here")

class ApiMeetingView(View):
    def get(self, request, meeting_id):
        meeting = Meeting.objects.filter(meeting_id=meeting_id).first()

        host_dict = {
            "id": meeting.host.id,
            "first_name": meeting.host.first_name,
            "last_name": meeting.host.last_name
        }

        persons = []
        for p in meeting.participants.all():
            eta = random.random() * 4
            persons.append({"id": p.id, "first_name": p.first_name, "last_name": p.last_name, "eta": eta})
        ret = {
            "titel": meeting.title,
            "id": meeting.meeting_id,
            "location": {"lat": meeting.location.lat, "lng": meeting.location.lng},
            "host": host_dict,
            "persons": persons
        }
        return JsonResponse(ret)

class NotifyHostView(View):
    def get(request, self, meeting_id, person_id):
        api = WebexTeamsAPI(access_token=settings.WEBEX_TEAMS_TOKEN)

        meeting = Meeting.objects.filter(meeting_id=meeting_id).first()
        person = Person.objects.filter(id=person_id).first()

        map_url = "http://192.168.1.246:8080/person/{}/map".format(person.id)
        msg = """
Hi {} your attendee **{}** for your meeting **{}** is lost. Fetch him! [Here]( {} ) is a link with his location. FYI, he might call you shortly.
        """.format(meeting.host.first_name, str(person), meeting.title, map_url)

        api.messages.create(toPersonEmail=meeting.host.mail, markdown=msg)
        mqtt_client = mqtt.Client(client_id="CSCO-MNEIDING")
        mqtt_client.connect("192.168.1.244")
        mqtt_client.publish("person/help", json.dumps({"first_name": person.first_name, "last_name": person.last_name}))

        return JsonResponse({"success": True})

class PersonMapView(View):
    def get(self, request, person_id):
        person = Person.objects.filter(id=person_id).first()

        if person is None:
            return HttpResponse("New server. Who dis?")

        ctx = {
            "persons": [person.id, ]
        }

        return render(request, "entities/meeting_map.html", ctx)

class PersonRetrieveView(View):
    def get(self, request, identification_type, identifier):
        person = None
        if identification_type == "mail":
            person = Person.objects.filter(mail=identifier).first()
        elif identification_type == "id":
            person = Person.objects.get(id=identifier)

        if person is None:
            return HttpResponse("error")
        else:
            person_dict = {
                'id': person.id,
                'first_name': person.first_name,
                'last_name': person.last_name,
                'mail': person.mail
            }

            return JsonResponse(person_dict)

class IPLinkView(View):
    def get(self, request, person_id, meeting_id):
        client_ip = request.META['REMOTE_ADDR']
        person = Person.objects.filter(id=person_id).first()
        meeting = Meeting.objects.filter(meeting_id=meeting_id).first()

        if person is None:
            return HttpResponse("New server. Who dis?")

        link = PersonIpLink.objects.filter(person=person).first()
        new_entry = False

        if link is None:
            link = PersonIpLink(person=person, ip=client_ip)
            new_entry = True
        link.save()
        person_dict = {
            'id': person.id,
            'first_name': person.first_name,
            'last_name': person.last_name,
            'mail': person.mail
        }

        ret = {
            "person": person_dict,
            "ip": client_ip,
            "new": new_entry,
            "meeting_id": str(meeting.meeting_id),
            "meeting_lat": meeting.location.lat,
            "meeting_lng": meeting.location.lng,
        }

        requests.post("http://192.168.1.244:5001/new-person", json=ret)

        return JsonResponse(ret)
