from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from .forms import CustomerRegistrationForm
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