from django.shortcuts import render, redirect
from cart.cart import Cart
from .forms import ShippingForm, PaymentForm
from .models import ShippingAddress, Order, OrderItem
from django.contrib.auth.models import User
from django.contrib import messages
from store.models import Product, Profile
import datetime


# Create your views here.


def orders(request, pk):
    if request.user.is_authenticated and request.user.is_superuser:

        # Get the order:
        order = Order.objects.get(id=pk)

        # Get the order items:
        items = OrderItem.objects.filter(order=pk)

        # In the below: If there is request.POST, then it means that the user has clicked on either of 'Mark As Shipped' or 'Mark As Shipped' button in the 'payment/orders.html' page which has the form method='POST'. This request.POST carried the name of the input form of the clicked button.
        if request.POST:
            status = request.POST['shipping_status']

            # Check if true or false:
            if status == 'true':

                # Get the order:
                order = Order.objects.filter(id=pk)

                # Update the status:
                now = datetime.datetime.now()
                order.update(shipped=True, date_shipped=now)

            else:
                # Get the order: 
                order = Order.objects.filter(id=pk)

                # Update the status:
                order.update(shipped=False)
            messages.success(request, 'Shipping Status Updated!')
            return redirect('home')

        return render(request, 'payment/orders.html', {"order": order, "items": items})

    else:
        messages.success(request, 'Access Denied!')
        return redirect('home')

def not_shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:

        # The below gives all the orders that are not shipped:
        orders = Order.objects.filter(shipped=False)

        # In the below: If there is request.POST, then it means that the user has clicked on 'Mark Shipped' button in the 'payment/not_shipped_dash.html' page which has the form method='POST'. This request.POST carried the name of the input form of the clicked button.
        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']

            # Get the order:
            order = Order.objects.filter(id=num)

            # Grab date and time:
            now = datetime.datetime.now()

            # Update order:
            order.update(shipped=True, date_shipped=now)

            # Redirect:
            messages.success(request, 'Shipping Status Updated!')
            return redirect('home')

        return render(request, 'payment/not_shipped_dash.html', {"order": order})
    else:
        messages.success(request, 'Access Denied!')
        return redirect('home')


def shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=True)

        # In the below: If there is request.POST, then it means that the user has clicked on 'Mark UnShipped' button in the 'payment/shipped_dash.html' page which has the form method='POST'. This request.POST carried the name of the input form of the clicked button.
        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']

            # Get the order:
            order = Order.objects.filter(id=num)

            # Grab date and time:
            now = datetime.datetime.now()

            # Update order:
            orders.update(shipped=False, date_shipped=now)

            # Redirect:
            messages.success(request, 'Shipping Status Updated!')
            return redirect('home')

        return render(request, 'payment/shipped_dash.html', {"orders": orders})
    else:
        messages.success(request, 'Access Denied!')
        return redirect('home')


def process_order(request):

    # 'if request.POST:' means it wants to find out 'if' there is the 'request.POST' dictionary which contains the billing details(in key-value pairs) of fields filled in the 'PaymentForm'('billing_form')) of the 'billing_info.html' page that would be processed by 'action="{% url 'process_order' %}' after clicking the 'Pay Now' button.
    if request.POST:

        # Get The Cart:
        cart = Cart(request)

        # Get the products in the cart:
        cart_products = cart.get_prods
        quantities = cart.get_quants
        totals = cart.cart_total()

        # GET BILLING INFO FROM THE LAST PAGE:
        # Here, for 'PaymentForm(request.POST)', we retrieve the form data stored in the request.POST dictionary Or for 'PaymentForm(None)' we do not have the form data stored in the request.POST, and so it gives no error even without the form data because None is an option.
        payment_form = PaymentForm(request.POST or None)

        # Get Shipping Session Data:
        # Get the 'ShippingForm' data from function- 'billing_info' below on this views.py file. 
        # This 'ShippingForm' data is given as 'my_shipping' after it has been saved in a session in function- 'billing_info' of this view.py page. Thus we need to get the shipping information as follows:
        my_shipping = request.session.get('my_shipping')

        # Gather Order Information:
        # 'shipping_full_name' and 'shipping_email' are got from 'ShippingForm' of forms.py of this app.
        # We need 'full_name', 'email', 'shipping_address' and 'amount_paid' because they are fields in the Order model of this app in models.py.
        full_name = my_shipping['shipping_full_name']
        email = my_shipping['shipping_email']

        # Create Shipping Address from session info:
        # We used f"" string because the data is much:
        shipping_address = f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_state']}\n{my_shipping['shipping_zipcode']}\n{my_shipping['shipping_country']}"

        amount_paid = totals

        # Create an Order:
        if request.user.is_authenticated:
            # logged in
            user = request.user

            # Create Order
            create_order = Order(user=user, full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()

            # Add order items:
            order_id = create_order.pk

            # Get product info:
            for product in cart_products():

                # Get product ID:
                product_id = product.id

                # Get product price:
                if product.is_sale:
                    price = product.sale_price
                else:
                    price = product.price

                # Get quantity:
                # remember that 'quantity'(that is 'cart.get_quants') in the above is given as 'self.cart' in 'cart.py' which is a key-value pair:
                # remember that for dictionaries, when looped we use: '.items':
                for key, value in quantities().items():
                    if int(key) == product_id:
                        # Create Order Item:
                        order_item = OrderItem(order_id=order_id, product_id=product_id, user=user, quantity=value, price=price)
                        order_item.save()

            # Delete the cart:
            # In function '__init__' which is in the 'cart.py' file of the 'cart' app, we have the session_key which is either already in 'request.session/self.session' or now created'. 
            # This 'session_key' is created in the self.session which is the current 'request.session'.
            # 'session_key' is the cart key used to create/store the cart in the session. 
            # And this session_key is in a dictionary format of key-value pairs (just as self.cart=cart).
            # So we need to delete the cart from the session using the session_key: 
            for key in list(request.session.keys()):
                # 'session' key is referenced from the function '__init__' which is in the 'cart.py' file of the 'cart' app.
                if key == "session_key":
                    del request.session[key]

            # Delete Cart from Database(old_cart field):
            current_user = Profile.objects.filter(user__id=request.user.id)

            # Delete Shopping Cart in Database(old_cart field):
            current_user.update(old_cart="")
            
            messages.success(request, 'Order Placed!')
            return redirect('home')
    
        else:
            # Create Order
            # No 'user' here because we are not logged in here.
            create_order = Order(full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()

            # Add order items:
            order_id = create_order.pk

            # Get product info:
            for product in cart_products():

                # Get product ID:
                product_id = product.id

                # Get product price:
                if product.is_sale:
                    price = product.sale_price
                else:
                    price = product.price

                # Get quantity:
                # remember that 'quantity'(that is 'cart.get_quants') in the above is given as 'self.cart' in 'cart.py' which is a key-value pair:
                # remember that for dictionaries, when looped we use: '.items':
                for key, value in quantities().items():
                    if int(key) == product_id:
                        # Create Order Item:
                        order_item = OrderItem(order_id=order_id, product_id=product_id, quantity=value, price=price)
                        order_item.save()


            # Delete the cart:
            # In function '__init__' which is in the 'cart.py' file of the 'cart' app, we have the session_key which is either already in 'request.session/self.session' or now created'. 
            # This 'session_key' is created in the self.session which is the current 'request.session'.
            # 'session_key' is the cart key used to create/store the cart in the session. 
            # And this session_key is in a dictionary format of key-value pairs (just as self.cart=cart).
            # So we need to delete the cart from the session using the session_key: 
            for key in list(request.session.keys()):
                # 'session' key is referenced from the function '__init__' which is in the 'cart.py' file of the 'cart' app.
                if key == "session_key":
                    del request.session[key]

            messages.success(request, 'Order Placed!')
            return redirect('home')

    else:
        messages.error(request, 'Access Denied!')
        return redirect('home')


def billing_info(request):
        
    # 'request.POST' is a dictionary containing key-value pairs of 'ShippingForm' details from 'checkout' after clicking the 'continue to billing' button on 'checkout.html' page. 
    # In other words 'request.POST' holds all the data filled in the 'ShippingForm' of the 'checkout' page.
    # 'request.POST' being a dictionary keeps the key-value pairs of the fields filled in the 'ShippingForm' of the 'checkout' page. And then passes the key-value pair form date to the 'billing_info' view here.
    if request.POST:

        # Copy these from the function-'checkout' below and edit:
        # Get The Cart:
        cart = Cart(request)

        # Get the products in the cart:
        cart_products = cart.get_prods
        quantities = cart.get_quants
        totals = cart.cart_total()


        # Create a session with Shipping Info:
        # Assign the form data in 'ShippingForm'(which is in 'checkout' page) which is stored in request.POST to  my_shipping:
        my_shipping = request.POST
        
        # Save the shipping information in the session:
        # 'request.session' is a dictionary that stores data when in the session. 
        # In the below,'my_shipping' is now a session that holds the 'ShippingForm' data filled by the user in the 'checkout' page.
        request.session['my_shipping'] = my_shipping

        
        #Check if the user is logged in: 
        # In the below: 'shipping_info' takes the value of 'request.POST'.
        # 'request.POST' is a dictionary of key-value pairs of details filled in by the user in 'shipping_form' of 'checkout.html' page.
        if request.user.is_authenticated:

            # Get the billing form:
            billing_form = PaymentForm()
            return render(request, 'payment/billing_info.html', {'cart_products': cart_products, 'quantities': quantities, 'totals': totals, 'shipping_info': request.POST, 'billing_form': billing_form})
        else:
            billing_form = PaymentForm()
            return render(request, 'payment/billing_info.html', {'cart_products': cart_products, 'quantities': quantities, 'totals': totals, 'shipping_info': request.POST, 'billing_form': billing_form})

        # shipping_form = request.POST
        # return render(request, 'payment/billing_info.html', {'cart_products': cart_products, 'quantities': quantities, 'totals': totals, 'shipping_form': shipping_form})
    else:
        messages.error(request, 'Access Denied!')
        return redirect('home')
    

def checkout(request):
    # Get The Cart:
    # Copy these from the function-'cart_summary' of the views.py file of cart app and edit:
    cart = Cart(request)
    # Get the products in the cart:
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totals = cart.cart_total()

    # 'request.user' is the current user of the site.'authenticated' means to be logged in.
    if request.user.is_authenticated:
        # checkout as logged in user:

        # Get current_user's shipping info first:
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)

        # USER'S SHIPPING FORM:
        #  The instance of the user is available since the user is logged in having his saved his shipping information in the database immediately after registering the first time.
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)

        return render(request, 'payment/checkout.html', {'cart_products': cart_products, 'quantities': quantities, 'totals': totals, 'shipping_form': shipping_form})
    else:
        # checkout as guest:

        # GET USER'S SHIPPING FORM:
        # No instance here because the guest has no saved information since they are not logged in.
        shipping_form = ShippingForm(request.POST or None)
        
        return render(request, 'payment/checkout.html', {'cart_products': cart_products, 'quantities': quantities, 'totals': totals, 'shipping_form': shipping_form})


def payment_success(request):
    return render(request, 'payment/payment_success.html', {})