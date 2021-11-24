
from django.contrib import admin
from django.urls import path, include

from main import views

urlpatterns = [
    path("saml2/", include("djangosaml2.urls")),
    path("", views.StartView.as_view(), name="start"),
    path("logged-in/", views.LoggedInView.as_view(), name="logged_in"),
]
