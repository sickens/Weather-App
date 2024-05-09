from django.urls import path
from . import views

urlpatterns = [
    path("", views.welcome, name="welcome"),
    path("current/", views.current, name="current"),
    path("forecast/", views.forecast, name="forecast"),
    path("precipitation/", views.precipitation, name="precipitation"),
]