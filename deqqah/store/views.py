from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import ProtectedError, Sum, Q, Avg, Count
from .forms import CustomerRegistrationForm, DeviceForm, OrderForm, StaffOrderForm, AccountForm
from .models import Customer, Device, OrderItem, ServiceOrder, Technician, ServiceType
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


@login_required
def order_list(request):
    orders = (
        ServiceOrder.objects.filter(device__customer__user=request.user)
        .select_related("device")
        .prefetch_related("items__service_type")
        .annotate(total=Sum("items__price"))
    )
    return render(request, "store/order_list.html", {"orders": orders})


@login_required
def order_create(request):
    customer = get_object_or_404(Customer, user=request.user)
    if not customer.devices.exists():
        messages.info(request, "Add a device before requesting a service.")
        return redirect("store:device_create")

    if request.method == "POST":
        form = OrderForm(request.POST)
        form.fields["device"].queryset = customer.devices.all()
        if form.is_valid():
            with transaction.atomic():
                order = form.save()
                for service in form.cleaned_data["services"]:
                    OrderItem.objects.create(
                    order=order, service_type=service, price=service.price
                )
            messages.success(request, "Your request has been submitted.")
            return redirect("store:order_list")
    else:
        form = OrderForm()
        form.fields["device"].queryset = customer.devices.all()

    return render(request, "store/order_form.html", {"form": form})


@login_required
def order_cancel(request, pk):
    order = get_object_or_404(
        ServiceOrder, pk=pk, device__customer__user=request.user
    )
    if not order.can_customer_cancel:
        messages.error(request, "This order can no longer be cancelled.")
        return redirect("store:order_list")

    if request.method == "POST":
        order.status = ServiceOrder.Status.CANCELLED
        order.save()
        messages.success(request, "Order cancelled.")
        return redirect("store:order_list")

    return render(request, "store/order_confirm_cancel.html", {"order": order})

@login_required
def staff_order_list(request):
    if not request.user.is_staff:
        raise PermissionDenied

    orders = ServiceOrder.objects.select_related(
        "device__customer", "technician"
    ).annotate(total=Sum("items__price"))

    status = request.GET.get("status", "")
    q = request.GET.get("q", "").strip()

    if status:
        orders = orders.filter(status=status)
    if q:
        orders = orders.filter(
            Q(device__customer__name__icontains=q)
            | Q(device__brand__icontains=q)
            | Q(device__model_name__icontains=q)
        )

    page = Paginator(orders, 5).get_page(request.GET.get("page"))

    return render(request, "store/staff_order_list.html", {
        "page": page,
        "status": status,
        "q": q,
        "statuses": ServiceOrder.Status.choices,
    })


@login_required
def staff_order_update(request, pk):
    if not request.user.is_staff:
        raise PermissionDenied
    order = get_object_or_404(ServiceOrder, pk=pk)
    if order.status == ServiceOrder.Status.CANCELLED:
        messages.error(request, "A cancelled order cannot be edited.")
        return redirect("store:staff_order_list")

    if request.method == "POST":
        form = StaffOrderForm(request.POST, instance=order)
        form.fields["technician"].queryset = Technician.objects.filter(is_active=True)
        if form.is_valid():
            form.save()
            messages.success(request, "Order updated.")
            return redirect("store:staff_order_list")
    else:
        form = StaffOrderForm(instance=order)
        form.fields["technician"].queryset = Technician.objects.filter(is_active=True)

    return render(request, "store/staff_order_form.html", {"form": form, "order": order})


@login_required
def reports(request):
    if not request.user.is_staff:
        raise PermissionDenied

    S = ServiceOrder.Status
    delivered = ServiceOrder.objects.filter(status=S.DELIVERED)

    # Aggregation: one number for the whole queryset
    revenue = OrderItem.objects.filter(order__status=S.DELIVERED).aggregate(
        total=Sum("price")
    )["total"] or 0
    delivered_count = delivered.count()
    average_order = delivered.annotate(total=Sum("items__price")).aggregate(
        avg=Avg("total")
    )["avg"] or 0

    # Annotation: one number for each technician
    technicians = Technician.objects.annotate(
        order_count=Count("orders"),
        in_progress_count=Count("orders", filter=Q(orders__status=S.IN_PROGRESS)),
    ).order_by("-order_count", "name")

    # Annotation: one number for each service
    counted = [S.REQUESTED, S.IN_PROGRESS, S.READY, S.DELIVERED]
    services = ServiceType.objects.annotate(
        times_requested=Count(
            "order_items", filter=Q(order_items__order__status__in=counted)
        ),
        delivered_revenue=Sum(
            "order_items__price", filter=Q(order_items__order__status=S.DELIVERED)
        ),
    ).order_by("-times_requested", "name")

    return render(request, "store/reports.html", {
        "revenue": revenue,
        "delivered_count": delivered_count,
        "average_order": average_order,
        "technicians": technicians,
        "services": services,
    })

def service_list(request):
    services = ServiceType.objects.filter(is_active=True)
    return render(request, "store/services.html", {"services": services})


@login_required
def account(request):
    customer = getattr(request.user, "customer", None)
    form = None
    if customer is not None:
        if request.method == "POST":
            form = AccountForm(request.POST, instance=customer)
            if form.is_valid():
                form.save()
                messages.success(request, "Your account was updated.")
                return redirect("store:account")
        else:
            form = AccountForm(instance=customer)
    return render(request, "store/account.html", {"form": form, "customer": customer})


class PasswordChange(SuccessMessageMixin, auth_views.PasswordChangeView):
    template_name = "store/password_change.html"
    success_url = reverse_lazy("store:account")
    success_message = "Your password was changed."