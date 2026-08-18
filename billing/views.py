from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from products.models import Product
from decimal import Decimal
import json


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
            items.append({'product': product, 'qty': qty, 'line_subtotal': line_subtotal, 'line_gst': line_gst})
        except Product.DoesNotExist:
            continue

    grand_total = (subtotal + gst_total).quantize(Decimal('0.01'))
    return {
        'items': items,
        'subtotal': subtotal.quantize(Decimal('0.01')),
        'gst_total': gst_total.quantize(Decimal('0.01')),
        'grand_total': grand_total,
    }


def serialize_cart(request, error=None):
    totals = get_cart_totals(request)
    return {
        'items': [
            {
                'barcode': item['product'].barcode,
                'name': item['product'].name,
                'qty': item['qty'],
                'price': str(item['product'].price),
                'gst': str(item['line_gst']),
                'line_total': str(item['line_subtotal']),
            }
            for item in totals['items']
        ],
        'subtotal': str(totals['subtotal']),
        'gst_total': str(totals['gst_total']),
        'grand_total': str(totals['grand_total']),
        'error': error,
    }


def index_view(request):
    return render(request, 'billing/react_app.html')


def api_cart(request):
    return JsonResponse(serialize_cart(request))


@csrf_exempt
def api_scan(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    data = json.loads(request.body or '{}')
    barcode = (data.get('barcode') or '').strip()
    cart = request.session.get('cart', {})
    error = None
    if barcode:
        try:
            Product.objects.get(barcode=barcode)
            cart[barcode] = cart.get(barcode, 0) + 1
            request.session['cart'] = cart
            request.session.modified = True
        except Product.DoesNotExist:
            error = f"No product found for barcode {barcode}"
    return JsonResponse(serialize_cart(request, error))


@csrf_exempt
def api_remove(request):
    """Remove one unit of an item; deletes the line once qty hits 0."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    data = json.loads(request.body or '{}')
    barcode = data.get('barcode', '')
    cart = request.session.get('cart', {})
    if barcode in cart:
        cart[barcode] -= 1
        if cart[barcode] <= 0:
            del cart[barcode]
        request.session['cart'] = cart
        request.session.modified = True
    return JsonResponse(serialize_cart(request))


@csrf_exempt
def api_delete_item(request):
    """Delete an item line entirely, regardless of quantity."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    data = json.loads(request.body or '{}')
    barcode = data.get('barcode', '')
    cart = request.session.get('cart', {})
    if barcode in cart:
        del cart[barcode]
        request.session['cart'] = cart
        request.session.modified = True
    return JsonResponse(serialize_cart(request))


@csrf_exempt
def api_clear(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    request.session['cart'] = {}
    return JsonResponse(serialize_cart(request))
