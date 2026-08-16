# Self Checkout — Indian Supermarket Billing App

A Django-based self-checkout system: scan a barcode, bill with GST, pay via UPI/card (Razorpay), get an emailed receipt.

## Features
- Product catalog with barcode, price, GST rate, and stock (managed via Django admin)
- Scan-to-cart flow with running GST-inclusive total
- Razorpay payment integration (UPI, cards, netbanking, wallets)
- Automatic stock deduction after a successful payment
- Transaction + line-item history (viewable in admin)
- Emailed receipt after checkout

## Project structure
```
selfcheckout/
├── manage.py
├── selfcheckout_config/     # Django project settings, URLs
├── products/                 # Product model + admin
├── billing/                  # Cart logic, Transaction/TransactionItem models
├── payments/                 # Razorpay integration, checkout & success views
```

## Prerequisites
- Python 3.11+
- A Razorpay account (test mode is free — https://dashboard.razorpay.com/signup)
- A Gmail account with an App Password, if you want real email receipts (optional — console backend works with zero setup)

## Setup (first time only)

1. **Activate the virtual environment** (PyCharm usually does this automatically when you open the project — check the terminal prompt shows `(.venv)`).

2. **Install dependencies:**
   ```
   .venv\Scripts\python.exe -m pip install django djangorestframework razorpay
   ```

3. **Apply database migrations:**
   ```
   .venv\Scripts\python.exe manage.py migrate
   ```

4. **Create an admin login** (if you don't already have one):
   ```
   .venv\Scripts\python.exe manage.py createsuperuser
   ```

5. **Add your Razorpay test keys** in `selfcheckout_config/settings.py`:
   ```python
   RAZORPAY_KEY_ID = "rzp_test_xxxxxxxxxxxx"
   RAZORPAY_KEY_SECRET = "your_secret_here"
   ```

6. **(Optional) Configure email** in `selfcheckout_config/settings.py`. For real Gmail sending:
   ```python
   EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
   EMAIL_HOST = 'smtp.gmail.com'
   EMAIL_PORT = 587
   EMAIL_USE_TLS = True
   EMAIL_USE_SSL = False
   EMAIL_HOST_USER = 'your_gmail@gmail.com'
   EMAIL_HOST_PASSWORD = 'your16digitapppassword'
   DEFAULT_FROM_EMAIL = 'Self Checkout Store <your_gmail@gmail.com>'
   ```
   For local testing without sending real emails, use instead:
   ```python
   EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
   ```
   (emails print to the terminal instead of actually sending)

## Running the app

**Always run on port 8080, not 8000** (port 8000 conflicts with another local service on this machine and causes an HTTPS redirect error).

```
.venv\Scripts\python.exe manage.py runserver 8080
```

Then open: **http://127.0.0.1:8080/**

Admin panel: **http://127.0.0.1:8080/admin/**

## Day-to-day workflow

- **Add products:** go to `/admin/`, click into "Products," click "Add Product." Fill in barcode, name, price, GST rate, stock.
- **Test the checkout flow:** on the main page, type a barcode (or scan with a real USB barcode scanner — it types automatically like a keyboard) and press Enter. Add an email if you want a receipt. Click "Pay Now."
- **Test payment (sandbox/test mode):**
  - Card: `5267 3181 8797 5449`
  - Expiry: any future date (e.g. `12/30`)
  - CVV: any 3 digits (e.g. `123`)
  - OTP if asked: `123456`
- **Check results:** after payment, view stock changes and transaction history at `/admin/products/product/` and `/admin/billing/transaction/`.

## After changing models

Any time you add or change a field in `models.py` (Product, Transaction, TransactionItem), run:
```
.venv\Scripts\python.exe manage.py makemigrations
.venv\Scripts\python.exe manage.py migrate
```

## Going live (real payments)

Currently running in Razorpay **test mode** — no real money moves. To accept real payments:
1. Complete KYC on the Razorpay dashboard (business PAN, bank details, GST if applicable)
2. Get live API keys (`rzp_live_...`) after verification
3. Swap `RAZORPAY_KEY_ID` / `RAZORPAY_KEY_SECRET` in settings.py to the live keys
4. Switch `EMAIL_BACKEND` to the real SMTP settings if still on console mode

## Known local quirks
- Port 8000 is occupied by something else on this machine and silently redirects to HTTPS — always use port 8080 instead.
- Browsers may cache an HTTPS redirect for `127.0.0.1` — if you ever see an SSL error, type `http://127.0.0.1:8080/` fresh into the address bar rather than clicking a bookmark.