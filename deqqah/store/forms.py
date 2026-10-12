from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction

from .models import Customer, Device

User = get_user_model()


class CustomerRegistrationForm(UserCreationForm):
    name = forms.CharField(max_length=100)
    phone = forms.CharField(max_length=20)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username",)

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        if Customer.objects.filter(phone=phone).exists():
            raise forms.ValidationError("This phone number is already registered.")
        return phone

    def save(self):
        with transaction.atomic():
            user = super().save()
            Customer.objects.create(
                user=user,
                name=self.cleaned_data["name"],
                phone=self.cleaned_data["phone"],
            )
        return user


class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ("brand", "model_name")
