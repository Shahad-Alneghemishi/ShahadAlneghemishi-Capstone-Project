from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.utils import timezone

from store.models import (
    Customer,
    Device,
    OrderItem,
    ServiceOrder,
    ServiceType,
    Technician,
)

User = get_user_model()
PASSWORD = "Capstone2026"  # fake demo password for every demo account

# True = delete all orders, devices, services, technicians and every non-staff user
# (customer accounts) first, then recreate the demo data. Staff and admin users are kept.
# Set to False to only add what is missing.
RESET = True

S = ServiceOrder.Status

CUSTOMERS = [  # username, name, phone
    ("reem", "Reem", "0550000001"),
    ("anas", "Anas", "0550000002"),
    ("faisal", "Faisal", "0550000003"),
    ("wed", "Wed", "0550000004"),  # Wed has no devices on purpose
]

DEVICES = [  # owner, brand, model
    ("Reem", "Dell", "OptiPlex 7090"),
    ("Reem", "Custom", "Gaming PC"),
    ("Anas", "HP", "ProDesk 400"),
    ("Faisal", "Lenovo", "ThinkCentre M70t"),
    ("Faisal", "Asus", "ROG Strix GT15"),
]

SERVICES = [  # name, price, description, is_active
    ("Cleaning", 100, "Dust removal for the case, fans and components.", True),
    ("Thermal Paste Replacement", 40, "Fresh thermal paste for lower processor temperatures.", True),
    ("OS Installation", 60, "Clean Windows installation with drivers.", True),
    ("Parts Assembly", 400, "We assemble the parts you bring into a working PC.", True),
    ("Windows 7 Installation", 50, "Legacy system installation.", False),  # inactive on purpose
]

TECHNICIANS = [  # name, is_active
    ("Samar", True),
    ("Ahmed", True),
    ("Hadeel", True),  # new technician, no orders on purpose
    ("Ali", False),  # inactive, only has an old delivered order
]

ORDERS = [  # device, technician, status, days ago created, days ago completed, services, customer note
    ("Dell OptiPlex 7090", "Samar", S.DELIVERED, 12, 10, ["Cleaning", "Thermal Paste Replacement"], ""),
    ("HP ProDesk 400", "Ahmed", S.DELIVERED, 9, 8, ["OS Installation"], ""),
    ("Lenovo ThinkCentre M70t", "Samar", S.DELIVERED, 8, 7, ["Cleaning"], ""),
    ("Custom Gaming PC", "Ali", S.DELIVERED, 20, 17, ["Parts Assembly"], "Parts brought by the customer."),
    ("Asus ROG Strix GT15", "Ahmed", S.IN_PROGRESS, 2, None, ["Cleaning", "OS Installation"], "The fans are very loud."),
    ("Custom Gaming PC", "Samar", S.IN_PROGRESS, 3, None, ["Thermal Paste Replacement"], "The computer overheats and shuts down."),
    ("HP ProDesk 400", "Ahmed", S.READY, 4, None, ["Cleaning"], ""),
    ("Lenovo ThinkCentre M70t", None, S.REQUESTED, 1, None, ["OS Installation", "Cleaning"], "The system is very slow, please reinstall Windows."),
    ("HP ProDesk 400", None, S.REQUESTED, 0.1, None, ["Thermal Paste Replacement"], ""),
    ("Dell OptiPlex 7090", None, S.CANCELLED, 6, None, ["Cleaning"], ""),
]


def make_user(username, is_staff=False):
    """Create the user if missing (existing users keep their password)."""
    user, created = User.objects.get_or_create(
        username=username, defaults={"is_staff": is_staff}
    )
    if created:
        user.set_password(PASSWORD)
        user.save()
    return user


if RESET:
    OrderItem.objects.all().delete()
    ServiceOrder.objects.all().delete()
    Device.objects.all().delete()
    User.objects.filter(is_staff=False).delete()  # also removes their customer records
    ServiceType.objects.all().delete()
    Technician.objects.all().delete()
    print("Old demo data removed.")

make_user("staff", is_staff=True)  # demo staff account

customers = {}
for username, name, phone in CUSTOMERS:
    customers[name], _ = Customer.objects.update_or_create(
        user=make_user(username), defaults={"name": name, "phone": phone}
    )

devices = {}
for owner, brand, model in DEVICES:
    devices[f"{brand} {model}"], _ = Device.objects.get_or_create(
        customer=customers[owner], brand=brand, model_name=model
    )

services = {}
for name, price, description, is_active in SERVICES:
    services[name], _ = ServiceType.objects.get_or_create(
        name=name,
        defaults={"price": price, "description": description, "is_active": is_active},
    )

technicians = {}
for name, is_active in TECHNICIANS:
    technicians[name], _ = Technician.objects.get_or_create(
        name=name, defaults={"is_active": is_active}
    )

if ServiceOrder.objects.exists():
    print("Orders already exist, skipping orders and items.")
else:
    now = timezone.now()
    for device, tech, status, created, completed, service_names, note in ORDERS:
        order = ServiceOrder.objects.create(
            device=devices[device],
            technician=technicians.get(tech),
            status=status,
            created_at=now - timedelta(days=created),
            completed_at=now - timedelta(days=completed) if completed is not None else None,
            customer_notes=note,
        )
        for service_name in service_names:
            service = services[service_name]
            OrderItem.objects.create(order=order, service_type=service, price=service.price)

# ---------- Checks against the expected results ----------
delivered = OrderItem.objects.filter(order__status=S.DELIVERED)
print("Delivered revenue (expected 700):", delivered.aggregate(total=Sum("price"))["total"])
print(
    "Orders per technician (expected Samar 3, Ahmed 3, Hadeel 0, Ali 1):",
    list(Technician.objects.annotate(n=Count("orders")).values_list("name", "n")),
)
print(
    "Items per service, cancelled included (expected Cleaning 6, Thermal Paste 3, OS 3, Parts 1, Windows 7 0):",
    list(ServiceType.objects.annotate(n=Count("order_items")).values_list("name", "n")),
)
print(
    "Orders by status (expected delivered 4, in_progress 2, ready 1, requested 2, cancelled 1):",
    dict(ServiceOrder.objects.values_list("status").annotate(n=Count("id")).order_by("status")),
)
print("Demo accounts: staff, reem, anas, faisal, wed")
