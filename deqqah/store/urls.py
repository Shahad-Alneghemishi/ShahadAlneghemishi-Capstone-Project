from django.urls import path
from . import views

app_name = "store"

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("devices/", views.device_list, name="device_list"),
    path("devices/add/", views.device_create, name="device_create"),
    path("devices/<int:pk>/edit/", views.device_update, name="device_update"),
    path("devices/<int:pk>/delete/", views.device_delete, name="device_delete")
]