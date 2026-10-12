from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import CustomerRegistrationForm, DeviceForm
from .models import Customer
# Create your views here.
def home(request):
    return render(request, "store/home.html")

def register(request):
    if request.method == "POST":
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Your account has been created.")
            return redirect("store:home")
    else:
        form = CustomerRegistrationForm()
    return render(request, "store/register.html", {"form": form})

@login_required
def device_list(request):
    customer = get_object_or_404(Customer, user=request.user)
    devices = customer.devices.all()
    return render(request, "store/device_list.html", {"devices": devices})

@login_required
def device_create(request):
    customer = get_object_or_404(Customer, user=request.user)
    if request.method == "POST":
        form = DeviceForm(request.POST)
        if form.is_valid():
            device = form.save(commit=False)
            device.customer = customer
            device.save()
            messages.success(request, "Device added.")
            return redirect("store:device_list")
    else:
        form = DeviceForm()
    return render(request, "store/device_form.html", {"form": form, "title": "Add a device"})