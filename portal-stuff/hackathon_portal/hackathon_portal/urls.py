"""hackathon_portal URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

import entities.views as EntitiesViews

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/meeting/<str:meeting_id>', EntitiesViews.ApiMeetingView.as_view()),
    path('person/<int:person_id>/map', EntitiesViews.PersonMapView.as_view()),
    path('meeting/<str:meeting_id>', EntitiesViews.MeetingView.as_view()),
    path('meeting/<str:meeting_id>/map', EntitiesViews.MeetingMapView.as_view()),
    path('meeting/<str:meeting_id>/person/<int:person_id>/navigate', EntitiesViews.NavigationView.as_view()),
    path('person/<int:person_id>/<str:meeting_id>/ip', EntitiesViews.IPLinkView.as_view()),
    path('person/<str:identification_type>/<str:identifier>', EntitiesViews.PersonRetrieveView.as_view()),
    path('notify/<str:meeting_id>/person/<int:person_id>', EntitiesViews.NotifyHostView.as_view()),
]

urlpatterns += staticfiles_urlpatterns()
