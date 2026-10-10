from django.contrib import admin
from .models import Customer, Device, ServiceType, Technician, ServiceOrder, OrderItem
# Register your models here.
admin.site.register(Customer)
admin.site.register(Device)
admin.site.register(ServiceType)
admin.site.register(Technician)
admin.site.register(ServiceOrder)
admin.site.register(OrderItem)