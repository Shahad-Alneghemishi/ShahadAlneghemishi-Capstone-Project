# Deqqah

A web application for a small PC cleaning and assembly shop. Customers request services online and follow their orders; staff process the orders and read simple reports.

## Problem and target users

Small PC repair shops usually take requests by phone or chat and track them on paper. Orders get lost, customers keep asking for updates, and the owner cannot see which services earn the most.

- **Customers** register, save their desktop PCs, request one or more services and follow the order status until delivery. They can cancel an order while it is still Requested.
- **Staff** see every order, search and filter it, assign a technician, change the status and read reports.

## Core features

- Registration and login with Django authentication (customer and staff roles, enforced on the server)
- Customer: device list, add, edit and delete; request a service with several services per order; My orders with totals; cancel a Requested order
- Staff: all orders with search, status filter and pagination; update an order (technician and status); reports page
- Reports: revenue of delivered orders and average order value (aggregation); orders per technician and requests and revenue per service (annotation)
- Business rules: a device with orders cannot be deleted; an order past Requested needs a technician; a delivered order gets its completion date automatically; only Requested orders can be cancelled by the customer; the price of each service is saved on the order when it is placed
- Account page: customers edit their name and phone, and every user can change the password
- Responsive layout for desktop and phone

## Versions

- Python 3.14
- Django 6.1.2
- SQLite (Django default)

## Setup

Run these commands from a terminal. `requirements.txt` is in the repository root; the Django project (`manage.py`) is in the `deqqah` folder.

```
git clone https://github.com/Shahad-Alneghemishi/ShahadAlneghemishi-Capstone-Project.git
cd ShahadAlneghemishi-Capstone-Project
python -m venv venv
```

Activate the environment:

- Windows PowerShell: `.\venv\Scripts\Activate.ps1`
- macOS / Linux: `source venv/bin/activate`

Then install the requirements and create the configuration file (see Configuration below):

```
python -m pip install -r requirements.txt
cd deqqah
copy .env.example .env
```

(On macOS / Linux use `cp .env.example .env`.) Edit `.env` and set a secret key, then migrate, load the sample data and start the server:

```
python manage.py migrate
python manage.py shell -c "exec(open('seed_data.py', encoding='utf-8').read())"
python manage.py runserver
```

Open http://127.0.0.1:8000/ in the browser.

### Configuration

Settings come from environment variables, read from a `.env` file placed next to `manage.py` (it is ignored by git). There is no default secret key: the project stops with a clear message if `DJANGO_SECRET_KEY` is missing.

| Variable | Meaning | Default |
|----------|---------|---------|
| `DJANGO_SECRET_KEY` | Secret key (required). Generate one with `python -c "import secrets; print(secrets.token_urlsafe(50))"` | none |
| `DJANGO_DEBUG` | `1` for local development | `0` |

Debug mode is off by default, so an unknown address shows the custom 404 page instead of Django's technical page. For local development set `DJANGO_DEBUG=1` in `.env`. To see the custom 404 page locally, set `DJANGO_DEBUG=0` and start the server with `python manage.py runserver --insecure` (the flag makes Django serve the CSS while debug is off), then open an address such as http://127.0.0.1:8000/zzz.

## Sample data and demo accounts

`seed_data.py` creates fictitious data: 4 customers, 5 devices, 5 services, 4 technicians and 10 orders that cover every status. Running it again resets the demo data (it removes all customer accounts, orders, devices, services and technicians first).

All demo accounts use the same fake password: `Capstone2026`. This is a demo project: use fictitious data when registering.

| Role | Username | Notes |
|------|----------|-------|
| Staff | `staff` | All orders, order update, reports |
| Customer | `reem` | Two devices, several orders |
| Customer | `anas` | One device, orders in several statuses |
| Customer | `faisal` | Two devices |
| Customer | `wed` | No devices (empty state) |

To use the Django admin site as well, create your own account:

```
python manage.py createsuperuser
```

## Reproducing the demonstration

1. Load the sample data as described in Setup and start the server.
2. As a visitor: open the home page, click Explore Services, then Request a Service, which leads to the registration page. Register a new customer with a fictitious name and phone number.
3. As the new customer: add a device, request two services (the prices are shown next to each service) and open My orders to see the order with status Requested.
4. Log out and log in as `staff`: open All orders, search and filter, then Update the new order: assign a technician, set In Progress, then Ready, then Delivered (the completion date is filled in automatically).
5. Log in as the customer again: the new status appears in My orders, and only Requested orders show a Cancel link.
6. Failure cases: as `reem`, try to delete the device that has orders (it is refused with a message). As `staff`, try to set a Requested order to In Progress without a technician (an error is shown).
7. As `staff`, open Reports: revenue and average order value, orders per technician, and requests and revenue per service. The figures change after step 4.

To return to the original demo data, run the sample data command again.

## Documentation

- [Entity relationship diagram](docs/erd.png)
- [Design notes: user journeys, wireframes, task list and database design decisions](docs/DESIGN.md)
- [Verification record](docs/TESTING.md)

## Market potential

- **Audience:** owners of small PC repair and assembly shops that still take requests by phone or chat.
- **Value:** one place for requests, clear order statuses for customers, and simple reports for the owner.
- **Language (assumption):** most customers in the target market read Arabic, so an Arabic interface is the first practical improvement.
- **Revenue model (assumption):** a monthly subscription per shop.
- **Evidence and assumptions:** the problem comes from how such shops usually work; no customer interviews or payment data exist yet, so demand and the subscription price are assumptions to be validated with real shops.

## Known limitations

- Desktop PCs only. Laptop support is a possible next improvement.
- The interface is in English only (the logo is bilingual). An Arabic interface is planned as the next improvement.
- No online payment and no email or SMS notifications.
- The sample data is fictitious.

## Next improvements

- Arabic interface with a language switch and a right-to-left layout: translate the templates and messages, and store translated names and descriptions for the services.
- Laptop support.
- Email or SMS notifications when the status of an order changes.

## Acknowledgements

I used Claude (Anthropic) as an AI assistant to plan the project, explain Django concepts, suggest code and draft documentation. I typed, tested and adapted the code myself and can explain it.
