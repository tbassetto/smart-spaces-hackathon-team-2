from django.contrib import admin

from .models import Location, Meeting, Person, PersonIpLink
# Register your models here.
admin.site.register(Location)
admin.site.register(Meeting)
admin.site.register(Person)
admin.site.register(PersonIpLink)
