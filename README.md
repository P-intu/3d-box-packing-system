# AI-Assisted Box Selection System

A robust Django & Django REST Framework application that selects the most suitable and cost-effective **single shipping box** for customer orders using a pure Python **3D Anchor / Extreme-Point First-Fit Decreasing** algorithm.

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Problem Statement](#problem-statement)
3. [Solution](#solution)
4. [Features](#features)
5. [Technology Stack](#technology-stack)
6. [Project Structure](#project-structure)
7. [Database Models](#database-models)
8. [API Endpoints](#api-endpoints)
9. [Order Flow](#order-flow)
10. [Box Recommendation Flow](#box-recommendation-flow)
11. [3D Anchor Packing Algorithm](#3d-anchor-packing-algorithm)
12. [Packing Assumptions & Box Selection Rules](#packing-assumptions--box-selection-rules)
13. [Installation & Setup](#installation--setup)
14. [Environment Variables](#environment-variables)
15. [Database Setup (SQLite & PostgreSQL)](#database-setup-sqlite--postgresql)
16. [Running the Server](#running-the-server)
17. [Running Tests](#running-tests)
18. [Example API Requests & Responses](#example-api-requests--responses)
19. [Limitations](#limitations)

---

## Project Overview
In ecommerce warehouse operations, determining the right shipping box for multi-item orders is crucial to reduce shipping costs and prevent packaging waste. This system automates the selection of the optimal single container for any customer order.

---

## Problem Statement
When a customer orders multiple products with varying quantities, dimensions, and weights:
- All items must fit within the internal physical dimensions of a single shipping box.
- The total weight of all items must not exceed the box's maximum weight capacity.
- The warehouse wants to minimize packaging cost and package volume.

---

## Solution
We implement an **automated box recommendation system** using the **3D Anchor / Extreme-Point First-Fit Decreasing** heuristic algorithm:
- Items are sorted in decreasing order of volume.
- Items are tested across all 6 orthogonal 3D orientations.
- Candidate boxes are sorted by volume (ascending) and cost (ascending).
- The smallest and lowest-cost suitable single box is recommended.

---

## Features
- **Full RESTful APIs**: CRUD endpoints for Products, Boxes, and Orders.
- **Dedicated Recommendation API**: Fast single-box recommendation for any order ID.
- **Pure Python 3D Packing**: No heavy external packing libraries or NumPy required.
- **Data Validation**: Strict dimension, weight, cost, and quantity validation.
- **Flexible Database**: Runs on SQLite3 by default, easily configured for PostgreSQL via `.env`.
- **Django Admin & Seeding**: Includes management commands for realistic sample data.
- **Comprehensive Test Suite**: Unit tests and API integration tests covering 33 scenarios.

---

## Technology Stack
- **Language**: Python 3.12+
- **Backend Framework**: Django 5.x
- **API Framework**: Django REST Framework (DRF)
- **Database**: SQLite3 (default) / PostgreSQL (supported)
- **Configuration**: `python-dotenv`

---

## Project Structure
```
Tradexa Assignment/
│
├── manage.py
├── requirements.txt
├── .gitignore
├── .env
├── README.md
│
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
└── box_selection/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── models.py
    ├── serializers.py
    ├── views.py
    ├── urls.py
    │
    ├── migrations/
    │   └── 0001_initial.py
    │
    ├── services/
    │   ├── __init__.py
    │   └── box_selector.py
    │
    ├── management/
    │   └── commands/
    │       ├── __init__.py
    │       └── seed_data.py
    │
    └── tests/
        ├── __init__.py
        ├── test_models.py
        ├── test_box_selector.py
        └── test_api.py
```

---

## Database Models

### 1. Product
Represents individual items that can be ordered.
- `id` (BigAutoField)
- `name` (CharField)
- `length`, `width`, `height` (DecimalField, $> 0$)
- `weight` (DecimalField, $> 0$)

### 2. Box
Represents available shipping boxes in the warehouse.
- `id` (BigAutoField)
- `name` (CharField)
- `internal_length`, `internal_width`, `internal_height` (DecimalField, $> 0$)
- `max_weight` (DecimalField, $> 0$)
- `cost` (DecimalField, $\ge 0$)

### 3. Order
Represents a customer order.
- `id` (BigAutoField)
- `created_at` (DateTimeField)

### 4. OrderItem
Links products and quantities to an order.
- `id` (BigAutoField)
- `order` (ForeignKey $\rightarrow$ Order, `CASCADE`)
- `product` (ForeignKey $\rightarrow$ Product, `CASCADE`)
- `quantity` (PositiveIntegerField, $\ge 1$)

---

## API Endpoints

### Products
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/products/` | List all products |
| `POST` | `/api/products/` | Create a product |
| `GET` | `/api/products/<id>/` | Retrieve a product |
| `PUT` | `/api/products/<id>/` | Update a product |
| `PATCH` | `/api/products/<id>/` | Partial update |
| `DELETE` | `/api/products/<id>/` | Delete a product |

### Boxes
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/boxes/` | List all boxes |
| `POST` | `/api/boxes/` | Create a box |
| `GET` | `/api/boxes/<id>/` | Retrieve a box |
| `PUT` | `/api/boxes/<id>/` | Update a box |
| `PATCH` | `/api/boxes/<id>/` | Partial update |
| `DELETE` | `/api/boxes/<id>/` | Delete a box |

### Orders
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/orders/` | List all orders |
| `POST` | `/api/orders/` | Create order with items |
| `GET` | `/api/orders/<id>/` | Retrieve an order |
| `PUT` | `/api/orders/<id>/` | Update an order |
| `PATCH` | `/api/orders/<id>/` | Partial update |
| `DELETE` | `/api/orders/<id>/` | Delete an order |

### Box Recommendation
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/orders/<order_id>/recommend-box/` | Recommend best single box for order |

---

## Order Flow
1. Customer places an order via `POST /api/orders/` providing a list of products and quantities.
2. An `Order` record and associated `OrderItem` records are created inside an atomic transaction.
3. The created order details are returned with nested item information.

---

## Box Recommendation Flow
1. User or warehouse system calls `POST /api/orders/<order_id>/recommend-box/`.
2. The view retrieves the order (or returns `404 Not Found`).
3. The view passes the order to `select_best_box(order)` in `services/box_selector.py`.
4. The service unpacks items, calculates total weight, evaluates candidate boxes, and tests 3D placement.
5. If a suitable box is found, serialized box details are returned; otherwise, a clear `None` response is returned.

---

## 3D Anchor Packing Algorithm
Located in: [`box_selection/services/box_selector.py`](box_selection/services/box_selector.py)

1. **Quantities Expansion**: Expand order quantities into individual items.
2. **Volume-Decreasing Sort**: Sort all items by volume ($L \times W \times H$) in descending order.
3. **Weight Filtering**: Filter out boxes where $\text{box.max\_weight} < \text{total\_order\_weight}$.
4. **Box Ordering**: Sort candidate boxes by:
   - Primary: Smallest internal volume ($L \times W \times H$)
   - Secondary: Lowest cost
5. **3D Anchor Placement**:
   - Start with initial anchor point `(0, 0, 0)`.
   - For each item, try all unique 3D axis-aligned rotations.
   - Test placement at existing anchor points sorted by lowest $(Z, Y, X)$.
   - Check bounding box limits and verify no 3D overlap with previously placed items.
   - Upon valid placement, add 3 new anchor points: $(x+L, y, z)$, $(x, y+W, z)$, $(x, y, z+H)$.
6. **Result**: First candidate box to pack all items is selected.

---

## Packing Assumptions & Box Selection Rules
- **Single Box**: Recommends exactly one container for all items in the order.
- **Axis-Aligned Rotations**: Items can be rotated in 6 orthogonal orientations.
- **Zero-Gap / Touching Allowed**: Items touching each other or the box walls are allowed.
- **No Overlap**: Items cannot occupy the same 3D space simultaneously.
- **Weight Limit**: Total weight of items cannot exceed the box's `max_weight`.

---

## Installation & Setup

### 1. Clone & Enter Repository
```bash
git clone <repo-url>
cd "Tradexa Assignment"
```

### 2. Create and Activate Virtual Environment
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Environment Variables
Create a `.env` file in the root directory:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Database Engine: 'sqlite' or 'postgresql'
DB_ENGINE=sqlite

# If DB_ENGINE=postgresql:
# DB_NAME=box_selection_db
# DB_USER=postgres
# DB_PASSWORD=postgres
# DB_HOST=localhost
# DB_PORT=5432
```

---

## Database Setup (SQLite & PostgreSQL)

### Run Migrations
```bash
python manage.py migrate
```

---

## Running the Server

### Start Development Server
```bash
python manage.py runserver
```
Server runs at: `http://127.0.0.1:8000/`

You can create your Products, Boxes, and Orders directly via the REST APIs or the Django Admin.

*(Optional) If you ever want preloaded sample data for quick testing:*
```bash
python manage.py seed_data
```

---

## Running Tests
Run all unit and API tests:
```bash
python manage.py test
```

---

## Example API Requests & Responses

### 1. Create an Order
`POST /api/orders/`
```json
{
  "items": [
    { "product": 1, "quantity": 1 },
    { "product": 3, "quantity": 2 }
  ]
}
```
**Response (`201 Created`):**
```json
{
  "id": 1,
  "created_at": "2026-10-07T00:31:00.123456Z",
  "items": [
    {
      "id": 1,
      "product": 1,
      "product_name": "Laptop",
      "quantity": 1
    },
    {
      "id": 2,
      "product": 3,
      "product_name": "Mouse",
      "quantity": 2
    }
  ]
}
```

### 2. Recommend Box for Order
`POST /api/orders/1/recommend-box/`

**Response (`200 OK` - Box Found):**
```json
{
  "success": true,
  "message": "Suitable box found.",
  "recommended_box": {
    "id": 2,
    "name": "Medium Box",
    "internal_length": "40.00",
    "internal_width": "30.00",
    "internal_height": "15.00",
    "max_weight": "10.00",
    "cost": "35.00"
  }
}
```

**Response (`200 OK` - No Suitable Box):**
```json
{
  "success": false,
  "message": "No suitable single box found for this order.",
  "recommended_box": null
}
```

---

## Limitations
- **Single-Box Only**: This system solves single-box packing recommendations. It does not perform multi-box bin packing or split orders across multiple packages.
- **Axis-Aligned Cuboids**: Items and boxes are assumed to be rectangular cuboids. Non-rectangular geometry, irregular shapes, or liquid packaging dynamics are not modeled.
