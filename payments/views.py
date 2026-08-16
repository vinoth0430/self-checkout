import razorpay
from django.conf import settings
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.template.loader import render_to_string

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def create_order(request):
    from billing.views import get_cart_totals
    totals = get_cart_totals(request)
    grand_total = totals['grand_total']
    email = request.GET.get('email', '').strip()

    amount_paise = int(grand_total * 100)

    order = client.order.create({
        "amount": amount_paise,
        "currency": "INR",
        "payment_capture": 1,
    })

    request.session['pending_order_id'] = order['id']

    return render(request, 'payments/checkout.html', {
        'order_id': order['id'],
        'amount': amount_paise,
        'key_id': settings.RAZORPAY_KEY_ID,
        'grand_total': grand_total,
        'email': email,
    })


@csrf_exempt
def payment_success(request):
    if request.method != 'POST':
        return redirect('cart')

    from billing.views import get_cart_totals
    from billing.models import Transaction, TransactionItem

    totals = get_cart_totals(request)
    order_id = request.session.get('pending_order_id', '')
    payment_id = request.POST.get('razorpay_payment_id', '')
    email = request.POST.get('email', '').strip()

    txn = Transaction.objects.create(
        razorpay_order_id=order_id,
        razorpay_payment_id=payment_id,
        customer_email=email,
        subtotal=totals['subtotal'],
        gst_total=totals['gst_total'],
        grand_total=totals['grand_total'],
    )

    for item in totals['items']:
        product = item['product']
        qty = item['qty']

        TransactionItem.objects.create(
            transaction=txn,
            product=product,
            product_name=product.name,
            quantity=qty,
            price_at_sale=product.price,
            gst_at_sale=item['line_gst'],
        )

        product.stock = max(0, product.stock - qty)
        product.save()

    if email:
        try:
            body = render_to_string('payments/receipt_email.txt', {'transaction': txn})
            send_mail(
                subject=f"Your receipt - Transaction #{txn.id}",
                message=body,
                from_email=None,
                recipient_list=[email],
            )
            print("EMAIL SENT SUCCESSFULLY")
        except Exception as e:
            print("EMAIL FAILED:", repr(e))

    request.session['cart'] = {}
    request.session.pop('pending_order_id', None)

    return render(request, 'payments/success.html', {'transaction': txn})