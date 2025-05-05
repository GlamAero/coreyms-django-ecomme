from django.shortcuts import render, get_object_or_404
from .cart import Cart
from store.models import Product
from django.http import JsonResponse
from django.contrib import messages

# Create your views here.

def cart_summary(request):
    # Get The Cart:
    cart = Cart(request)

    # Get the products in the cart:
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totals = cart.cart_total()
    return render(request, 'cart_summary.html', {'cart_products': cart_products, 'quantities': quantities, 'totals': totals})


def cart_add(request):
    #Get The Cart:
    cart = Cart(request)

    # test for POST: (# action == 'post' is at the product.html file at the ajax.js section):
    if request.POST.get('action') == 'post':

        # Get stuff: (the 'product_id' and 'product_qty' below is got from the product.html file at the ajax.js section of the javascript section): 
        # 'request.POST.get' is getting its content from the dictionary, since request.POST after being posted, stores its content in a dictionary format.
        # All data retrieved from 'request.POST.get()' is in string format, so you might need to cast it to other types (e.g., int ) if required, as rbelow:
        product_id = int(request.POST.get('product_id'))

        product_qty = int(request.POST.get('product_qty'))

        # Look up the product in the database whose id=product_id above:
        product = get_object_or_404(Product, id=product_id)

        # Save to session: ('add' is a function in cart.py file)
        cart.add(product=product, quantity=product_qty)


        # To make the cart icon to function to increase or decrease values:
        # Get the number of unique products selected from cart.py in the ' __len__' function: 
        # This for the cart icon increment or decrement values in quantity: 
        # It indicates how many products are in the cart:
        cart_quantity = cart.__len__()

        # Return response:
        # This 'qty' is referenced in product.py file in the 'success' area of ajax.js section of the javascript section.
        response = JsonResponse({'qty': cart_quantity})
        messages.success(request, ("Product Added To Cart..."))

        return response
        # Each content of this function is referenced in the 'product.html' page of the 'store' app.


def cart_delete(request):
    cart = Cart(request)

    if request.POST.get('action') == 'post':

        # Get stuff: (the 'product_id' and 'product_qty' below is got from the product.html file at the ajax.js section of the javascript section): 
        # 'request.POST.get' is getting from the dictionary since request.POST after being posted stores its content in a dictionary format.
        # All data retrieved from 'request.POST.get()' is in string format, so you might need to cast it to other types (e.g., int ) if desired:
        product_id = int(request.POST.get('product_id'))
        
        product = Product.objects.get(id=product_id)

        # Call delete Function in Cart
        cart.delete(product=product_id)

        response = JsonResponse({'product': product_id})

        messages.success(request, f"'{product.name}' Removed From Your Shopping Cart...")

        return response
        #return redirect('cart_summary')


def cart_update(request):
    cart = Cart(request)

    if request.POST.get('action') == 'post':

        # Get stuff: (the 'product_id' and 'product_qty' below is got from the product.html file at the ajax.js section of the javascript section): 
        # 'request.POST.get' is getting from the dictionary since request.POST after being posted stores its content in a dictionary format.
        # All data retrieved from 'request.POST.get()' is in string format, so you might need to cast it to other types (e.g., int ) if desired:
        product_id = int(request.POST.get('product_id'))

        product_qty = int(request.POST.get('product_qty'))

        cart.update(product=product_id, quantity=product_qty)

        response = JsonResponse({'qty': product_qty})

        messages.success(request, ("Your Cart Has Been Updated..."))

        return response
        #return redirect('cart_summary')


