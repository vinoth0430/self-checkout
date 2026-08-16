from django.shortcuts import render, redirect
from products.models import Product
from decimal import Decimal


def get_cart_totals(request):
    cart = request.session.get('cart', {})
    items = []
    subtotal = Decimal('0.00')
    gst_total = Decimal('0.00')

    for barcode, qty in cart.items():
        try:
            product = Product.objects.get(barcode=barcode)
            line_subtotal = product.price * qty
            line_gst = ((line_subtotal * product.gst_rate) / Decimal('100')).quantize(Decimal('0.01'))
            subtotal += line_subtotal
            gst_total += line_gst
            items.append({
                'product': product, 'qty': qty,
                'line_subtotal': line_subtotal, 'line_gst': line_gst,
            })
        except Product.DoesNotExist:
            continue

    grand_total = (subtotal + gst_total).quantize(Decimal('0.01'))
    return {
        'items': items,
        'subtotal': subtotal.quantize(Decimal('0.01')),
        'gst_total': gst_total.quantize(Decimal('0.01')),
        'grand_total': grand_total,
    }


def cart_view(request):
    cart = request.session.get('cart', {})

    if request.method == 'POST':
        if 'clear' in request.POST:
            request.session['cart'] = {}
            return redirect('cart')

        barcode = request.POST.get('barcode', '').strip()
        if barcode:
            try:
                product = Product.objects.get(barcode=barcode)
                cart[barcode] = cart.get(barcode, 0) + 1
                request.session['cart'] = cart
                request.session.modified = True
            except Product.DoesNotExist:
                request.session['last_error'] = f"No product found for barcode {barcode}"
        return redirect('cart')

    error = request.session.pop('last_error', None)
    totals = get_cart_totals(request)
    totals['error'] = error
    return render(request, 'billing/cart.html', totals)