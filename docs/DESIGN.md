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

Simple text wireframes of the main screens.

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
| 2 | Responsive CSS | Done |
| 2 | README, sample data and fresh setup check | Done |
| 2 | Verification record | Done |
| 3 | Future: Arabic interface, laptop support, notifications, online payment, order detail page | Not planned for this version |

Blockers: none.

## Database design decisions

Relationships and deletion behaviour

| Relationship | Choice | Reason |
|--------------|--------|--------|
| Customer to login account | OneToOne, CASCADE | Each customer has exactly one account, and staff accounts have no customer. If the account is removed, the profile has no use. |
| Device to customer | ForeignKey, PROTECT | A customer has many devices and a device has one owner. A customer with devices cannot be deleted by mistake. |
| Order to device | ForeignKey, PROTECT | An order belongs to one device. The customer is found through the device, so the same fact is stored in one place only. A device with orders cannot be deleted, which keeps the history and the revenue. |
| Order to technician | ForeignKey, SET_NULL, optional | An order exists before a technician is assigned. If a technician is removed the order stays. Normally a technician is deactivated with `is_active` instead of deleted. |
| Order item to order | ForeignKey, CASCADE | An item has no meaning without its order. |
| Order item to service | ForeignKey, PROTECT | Old orders keep the service they used. A service is retired with `is_active` instead of deleted. |
| Order and service | Many-to-many through `OrderItem` | An order has several services and a service appears in many orders. The junction table also stores the price. |

Constraints and rules

| Rule | Where | Reason |
|------|-------|--------|
| Phone number unique, service name unique, one service once per order | Database (unique) | The database refuses duplicates from any source. |
| Price is not negative, completion date is not before the creation date | Database (check constraint) | Last line of defence for bad values. |
| A delivered order needs a completion date; an order past Requested needs a technician | `clean()` of the order | These rules compare several fields, and `clean()` shows a clear message in the forms and the admin. |

Field types

| Field | Type | Reason |
|-------|------|--------|
| Ids and foreign keys | Integer, generated by Django | They only identify records. They are the only integers in the schema. |
| Prices | Decimal (8 digits, 2 decimals) | Money must be exact. A float can give rounding errors. |
| Price on the order item | Decimal, copied from the service | A snapshot of the price when the order was placed, so changing a service price later does not change old orders. |
| Phone number | Text, not integer | It keeps the leading zero and is not used in calculations. |
| Status | Text with a fixed list of choices | Only valid statuses are accepted and the labels stay readable. |
| Notes | Long text, optional | Free text of any length. |
| Dates | Date and time; completion date optional | An order may not be finished yet. |
| `is_active` | Boolean | Retire a service or technician without losing history. |

Order totals are not stored. They are calculated from the items with aggregation and annotation, so they cannot disagree with the items.
