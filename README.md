# Smart Goldsmith Management & Jewellery Customization System

A Django-based web application for digitizing goldsmith/jewellery business operations —
customer catalogue browsing, jewellery customization requests, automatic gold-rate based
pricing, order tracking, inventory, and payments.

## Tech Stack
- **Backend:** Python, Django
- **Frontend:** HTML, Bootstrap 5, JavaScript
- **Database:** SQLite (default, zero setup) — switchable to MySQL
- **Charts:** Chart.js (business dashboard)

## Features

**Customer side**
- Registration/login, profile management
- Browse & search jewellery catalogue
- Request custom jewellery (with reference image upload)
- Live price estimates (weight × gold rate + making charge + GST)
- Place orders, track status, view payment history

**Goldsmith/admin side**
- Manage jewellery catalogue & categories
- Update daily gold/silver rates
- Review and price customization requests
- Track and update order status (placed → production → delivered)
- Manage raw material inventory (with low-stock alerts)
- Record payments (advance/final)
- Business dashboard with sales & order-status charts

## Project Structure

```
goldsmith_project/
├── accounts/        # custom User model (customer/goldsmith roles), auth
├── catalogue/       # Category, Jewellery, GoldRate + price calculator
├── customization/   # custom jewellery request workflow
├── orders/          # order placement & status workflow
├── payments/        # payment recording, linked to orders
├── inventory/       # raw material stock tracking
├── dashboard/        # role-aware home page + Chart.js reports
├── templates/        # all HTML templates (Bootstrap)
└── goldsmith/        # project settings/urls
```

## Setup

1. **Clone and enter the project**
   ```bash
   git clone <your-repo-url>
   cd goldsmith_project
   ```

2. **Create a virtual environment and install dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Run migrations**
   ```bash
   python manage.py migrate
   ```

4. **Create an admin/goldsmith account**
   ```bash
   python manage.py createsuperuser
   ```
   Then, to make that account a "goldsmith" (business-side) role, run:
   ```bash
   python manage.py shell -c "from accounts.models import User; u=User.objects.get(username='YOUR_USERNAME'); u.role='goldsmith'; u.save()"
   ```

5. **Run the dev server**
   ```bash
   python manage.py runserver
   ```
   Visit `http://127.0.0.1:8000/`

## Switching to MySQL

By default this project uses SQLite so it runs with zero setup. To use MySQL
(matching the original tech-stack proposal):

1. `pip install mysqlclient` (needs MySQL dev headers on your system)
2. Set the environment variable `USE_MYSQL=1` and provide `DB_NAME`, `DB_USER`,
   `DB_PASSWORD`, `DB_HOST`, `DB_PORT` (see `goldsmith/settings.py`)
3. Re-run `python manage.py migrate`

## Price Calculation

The pricing formula (see `catalogue/models.py :: calculate_price`):

```
metal_cost = weight_in_grams × current_rate_per_gram
subtotal   = metal_cost + making_charge
GST        = subtotal × GST_percent
total      = subtotal + GST
```

The current gold/silver rate is whatever the goldsmith last entered under
**Manage → Gold Rates**.

## Notes for submission / demo

- Seed at least one `GoldRate` before browsing the catalogue, or prices will
  show as "unavailable".
- The `Order.status` field models the workflow from the proposal:
  `placed → advance_paid → in_production → ready → delivered` (or `cancelled`).
- `DEBUG = True` and the default `SECRET_KEY` are fine for local dev/demo but
  must be changed before any real deployment.

## Future Enhancements (from the original proposal)
- AI-based jewellery design recommendations
- Image-based jewellery search
- Android app
- Online payment gateway integration
- SMS/email/app notifications
