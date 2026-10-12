from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import ProtectedError
from .forms import CustomerRegistrationForm, DeviceForm
from .models import Customer, Device
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


@login_required
def device_update(request, pk):
    device = get_object_or_404(Device, pk=pk, customer__user=request.user)
    if request.method == "POST":
        form = DeviceForm(request.POST, instance=device)
        if form.is_valid():
            form.save()
            messages.success(request, "Device updated.")
            return redirect("store:device_list")
    else:
        form = DeviceForm(instance=device)
    return render(request, "store/device_form.html", {"form": form, "title":"Edit device"})

@login_required
def device_delete(request, pk):
    device = get_object_or_404(Device, pk=pk, customer__user=request.user)
    if request.method == "POST":
        try:
            device.delete()
            messages.success(request, "Device deleted.")
        except ProtectedError:
            messages.error(request, "This device has service orders, so it cannot be deleted.")
        return redirect("store:device_list")
    return render(request, "store/device_confirm_delete.html", {"device": device})