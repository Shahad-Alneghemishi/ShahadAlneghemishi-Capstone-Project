from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import F, Q, Sum
from django.utils import timezone

# Create your models here.
class Customer(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="customer"
    )
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Device(models.Model):
    class DeviceType(models.TextChoices):
        DESKTOP = "desktop", "Desktop"
        LAPTOP = "laptop", "Laptop"

    customer = models.ForeignKey(
        Customer, on_delete=models.PROTECT, related_name="devices"
    )
    device_type = models.CharField(
        max_length=10, choices=DeviceType.choices, default=DeviceType.DESKTOP
    )
    brand = models.CharField(max_length=50)
    model_name = models.CharField(max_length=80)

    class Meta:
        ordering = ["customer__name", "brand"]

    def __str__(self):
        return f"{self.brand} {self.model_name} ({self.customer})"


class ServiceType(models.Model):
    name = models.CharField(max_length=80, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.CheckConstraint(
                condition=Q(price__gte=0), name="servicetype_price_non_negative"
            )
        ]

    def __str__(self):
        return self.name


class Technician(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

class ServiceOrder(models.Model):
    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        IN_PROGRESS = "in_progress", "In Progress"
        READY = "ready", "Ready for pickup"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    device = models.ForeignKey(
        Device, on_delete=models.PROTECT, related_name="orders"
    )
    technician = models.ForeignKey(
        Technician, on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders"
    )
    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.REQUESTED
    )
    created_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    customer_notes = models.TextField(blank=True)
    staff_notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=Q(completed_at__isnull=True) |
                Q(completed_at__gte=F("created_at")),
                name="order_completed_after_created",
            )
        ]
    def clean(self):
        if self.completed_at and self.completed_at < self.created_at:
            raise ValidationError("Completion date cannot be before the request date.")
        if self.status == self.Status.DELIVERED and not self.completed_at:
            raise ValidationError("A delivered order must have a completion date.")

    @property
    def can_customer_cancel(self):
        return self.status == self.Status.REQUESTED

    @property
    def total_price(self):
        return self.items.aggregate(total=Sum("price"))["total"] or 0

    def __str__(self):
        return f"Order #{self.pk} - {self.device}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        ServiceOrder, on_delete=models.CASCADE, related_name="items"
    )
    service_type = models.ForeignKey(
        ServiceType, on_delete=models.PROTECT, related_name="order_items"
    )
    price = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["order", "service_type"], name="unique_service_per_order"
            )
        ]

    def __str__(self):
        return f"{self.service_type} x {self.order_id}"