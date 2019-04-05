from django.db import models
from webexteamssdk import WebexTeamsAPI
from django.conf import settings

from django.dispatch import receiver
from django.db.models.signals import post_save

import uuid

# Create your models here.
class Person(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    mail = models.EmailField()

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)

class Location(models.Model):
    name = models.CharField(max_length=100)
    floor = models.IntegerField(default=1)
    share_poi = models.IntegerField(default=0)
    lat = models.FloatField(default=0.0)
    lng = models.FloatField(default=0.0)

    def get_mazemap_url(self):
        return "https://use.mazemap.com/#v=1&sharepoitype=poi&sharepoi={}".format(self.share_poi)

    def __str__(self):
        return "{} ({})".format(self.name, self.floor)

class Meeting(models.Model):
    host = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="host")
    title = models.CharField(max_length=150)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    date = models.DateField()
    time_start = models.TimeField()
    time_end = models.TimeField()
    participants = models.ManyToManyField(Person, related_name="participants")
    meeting_id = models.UUIDField(editable=False)

    def __str__(self):
        return "{} ({} – {})".format(self.title, self.time_start, self.time_end)

    def get_meeting_link(self):
        return "{}/meeting/{}".format(settings.BASE_URL, self.meeting_id)

    def get_participant_ids(self):
        return [p.id for p in self.participants.all()]

class PersonIpLink(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    ip = models.GenericIPAddressField()
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{} -> {}".format(self.person, self.ip)

@receiver(post_save, sender=Meeting)
def create_user_profile(sender, instance, created, **kwargs):
    if created or True:
        api = WebexTeamsAPI(access_token=settings.WEBEX_TEAMS_TOKEN)
        host = instance.host
        msg = "Hi {}! We just created your meeting **{}** from **{}** to **{}** <br> The link to the meeting is here: {}".format(host.first_name, instance.title, instance.time_start, instance.time_end, instance.get_meeting_link())
        api.messages.create(toPersonEmail=instance.host.mail, markdown=msg)
        api.messages.create(toPersonEmail=instance.host.mail, markdown="Do you want us to create WiFi access codes for your visitors?")
