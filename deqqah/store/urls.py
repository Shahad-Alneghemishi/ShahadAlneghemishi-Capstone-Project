from django.urls import path
from . import views

app_name = "store"

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("devices/", views.device_list, name="device_list"),
    path("devices/add/", views.device_create, name="device_create"),
    path("devices/<int:pk>/edit/", views.device_update, name="device_update"),
    path("devices/<int:pk>/delete/", views.device_delete, name="device_delete"),
    path("orders/", views.order_list, name="order_list"),
    path("orders/new/", views.order_create, name="order_create"),
    path("orders/<int:pk>/cancel/", views.order_cancel, name="order_cancel"),
    path("staff/orders/", views.staff_order_list, name="staff_order_list"),
    path("staff/orders/<int:pk>/edit/", views.staff_order_update, name="staff_order_update"),
    path("staff/reports/", views.reports, name="reports"),
    path("services/", views.service_list, name="service_list"),
]