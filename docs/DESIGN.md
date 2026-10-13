# Design Notes - Deqqah

Deqqah manages PC cleaning and assembly services for a small repair shop. Customers request services online; staff process the orders and read simple reports.

## User journeys

**Customer**

1. Register with name, phone, username and password. The customer is logged in automatically.
2. Add a desktop PC (brand and model).
3. Request a service: choose a device, tick one or more services, add an optional note. The order is saved with status Requested.
4. Follow the order in My orders (status, services, total).
5. Cancel the order while it is still Requested.

**Staff**

1. Log in.
2. Open All orders, search by customer or device, filter by status.
3. Update an order: assign an active technician and change the status. Delivered fills the completion date automatically.
4. Open Reports: revenue, technician workload and service demand.

## Wireframes

My orders

```
+--------------------------------------------------+
| Home | My devices | My orders | Log out           |
+--------------------------------------------------+
| My orders                    [Request a service] |
|                                                  |
| Order #11 - HP ProDesk 400 - Requested           |
|   Cleaning ........................... 100.00    |
|   Thermal Paste Replacement ........... 40.00    |
|   Total: 140              [Cancel order]         |
+--------------------------------------------------+
```

Request a service

```
+--------------------------------------------------+
| Request a service                                |
| Device:  [ HP ProDesk 400            v ]         |
| Notes:   [                             ]         |
| Services: [x] Cleaning                           |
|           [ ] OS Installation                    |
|           [x] Thermal Paste Replacement          |
| [Submit request]  Cancel                         |
+--------------------------------------------------+
```

All orders (staff)

```
+--------------------------------------------------+
| Search [__________]  Status [All v] [Filter] Reset|
| # | Customer | Device | Status | Tech | Total | . |
| 1 | Reem     | Dell.. | Deliv. | Samar| 140   |Upd|
| 6 | Reem     | Custom | In Pr. | Samar| 40    |Upd|
|                  Previous  Page 1 of 2  Next     |
+--------------------------------------------------+
```

Reports (staff)

```
+--------------------------------------------------+
| Revenue: 700 | Delivered orders: 4 | Average: 175|
| Technician workload   (name, orders, in progress)|
| Services              (requested, revenue)       |
+--------------------------------------------------+
```

## Prioritized task list

| Priority | Task | Status |
|----------|------|--------|
| 1 | Models, migrations and ERD | Done |
| 1 | Registration and login (Django authentication) | Done |
| 1 | Device list, add, edit and delete | Done |
| 1 | Order creation, My orders and cancellation | Done |
| 1 | Staff order list (search, filter, pagination) and order update | Done |
| 1 | Reports with aggregation and annotation | Done |
| 2 | Responsive CSS | In progress |
| 2 | README, sample data and fresh setup check | To do |
| 2 | Verification record | In progress |
| 2 | Demo preparation | To do |
| 3 | Future: laptop support, notifications, online payment, order detail page | Not planned for this version |

Blockers: none.
