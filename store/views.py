from django.shortcuts import render, redirect
from .models import Product, Category, Profile
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm
from payment.forms import ShippingForm
from payment.models import ShippingAddress
from django import forms
from django.db.models import Q
import json
from cart.cart import Cart



def search(request):
    #Determine if they filled out the form:
    if request.method == 'POST':
        # 'searched' because 'searched' is given as the name of the input in the 'search.html' file
        # 'request.POST' contains the search word sent to the server. 'request.POST' holds what the user fills in the searchbar input field.
        searched = request.POST['searched']

        # Query The Products DB Model:
        # 'icontains' is used to perform a case-insensitive search for the specified string within the field. And to search for content within the specified string
        # 'Q' is used to search for multiple fields at once. It allows you to combine multiple conditions using the OR operator.
        searched = Product.objects.filter(Q(name__icontains=searched) | Q(description__icontains=searched) | Q(category__name__icontains=searched))

        # Test for null:
        if not searched:
            messages.error(request, "That Product Does Not Exist... Please Try Again")
            return render(request, 'search.html', {})
        else:
            return render(request, 'search.html', {'searched': searched})
    else:
        return render(request, 'search.html', {})


# Here we are adding more features to the user profile. A new page('Update Info') is now created for that:
# 'update_info' view's content was copied from 'update_user' view's content and edited
def update_info(request):
    # 'request.user' is the current user of the site.'authenticated' means to be logged in.
    if request.user.is_authenticated:
        # Get the current user:
        # For a new user, the 'Profile' object is empty because the user is yet to fill the 'UserInfoForm'.
        current_user = Profile.objects.get(user__id=request.user.id)
        
        # Get current_user's shipping info:
        # For a new user, the 'ShippingAddress' object is empty because the user is yet to fill the 'ShippingForm'.
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)

        # GET ORIGINAL USER FORM:
        # 'request.POST' contains the form data submitted to the server via an HTTP POST request.
        # When the form is submitted (e.g., user clicks the submit button), 'request.POST' will contain the submitted data
        # When the form is not submitted (e.g., the page is just loaded), 'None' is passed to the form. This ensures the form is displayed empty (or pre-filled if it's bound to an instance). With 'None', it works even if there is no data bound to the request.POST, meaning it gives no error since it gives room for None as value.
        form = UserInfoForm(request.POST or None, instance=current_user)

        # GET USER'S SHIPPING FORM:
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)

        if form.is_valid() or shipping_form.is_valid():
            # Save original form:
            form.save()

            # Save shipping form:
            shipping_form.save()

            messages.success(request, "Your Info Has Been Updated Successfully!")
            return redirect('home')
        
        # If the form is not valid, that is if 'request.POST' is None, do the following:(meaning if the user opened the page but he is not editing the form and submitting data):
        return render(request, 'update_info.html', {'form': form, 'shipping_form': shipping_form})
    else:
        messages.error(request, "You must be logged in to update your profile.")
        return redirect('home')
    

# Create your views here.

# To update/change password after registering/login
def update_password(request):
    if request.user.is_authenticated:
        current_user = request.user

        # Did they fill out the form:
        if request.method == 'POST':
            form = ChangePasswordForm(current_user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Your Password Has Been Updated...") 
                login(request, current_user)
                return redirect('update_user')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                    return redirect('update_password')

        else:
            form = ChangePasswordForm(current_user)
            return render(request, "update_password.html", {'form': form})
    else:
        messages.error(request, "You Must Be Logged In To View That Page")
        return redirect('home')


# To create the user profile:
def update_user(request):
    # 'request.user' is the current user of the site.'authenticated' means to be logged in.
    if request.user.is_authenticated:
        # For a new user, the 'User' object is not empty because the user has already filled the 'SignUpForm' when registering. And data filled by the current user/new user in the form is used to create the profile here. 
        # 'User' here is the model of the currently signed up user with his details
        current_user = User.objects.get(id=request.user.id)

        # 'request.POST' contains the form data submitted to the server via an HTTP POST request.
        # When the form is submitted (e.g., user clicks the submit button),  will contain the submitted data
        # When the form is not submitted (e.g., the page is just loaded), 'None' is passed to the form. This ensures the form is displayed empty (or pre-filled if it's bound to an instance). With 'None', it works even if there is no data bound to the request.POST, meaning it gives no error since it gives room for None as value.
        user_form = UpdateUserForm(request.POST or None, instance=current_user)

        if user_form.is_valid():
            user_form.save()

            login(request, current_user)  # Re-login the user to update session data
            messages.success(request, "User Has Been Updated Successfully!")
            return redirect('home')
        
        # If the form is not valid, that is if 'request.POST' is None, do the following:(meaning if the user opened the page but he is not editing the form and submitting data):
        return render(request, 'update_user.html', {'user_form': user_form})
    else:
        messages.error(request, "You must be logged in to update your profile.")
        return redirect('home')


def category_summary(request):
    categories = Category.objects.all()
    return render(request, 'category_summary.html', {'categories': categories})


def category(request, foo):
    # Replace hyphens(for those category names with '-') with spaces in the url when passed:
    foo = foo.replace('-', ' ')

    #Grab the Category from the url:
    try:
        # Look Up The Category
        category = Category.objects.get(name=foo)
        products = Product.objects.filter(category=category)
        return render(request, 'category.html', {'category': category, 'products': products})
    except:
        messages.success(request, ("That Category Doesn't Exist..."))
        return redirect('home')


def product(request, pk):
    product = Product.objects.get(id=pk)
    return render(request, 'product.html', {'product': product})


def home(request):
    products = Product.objects.all()
    return render(request, 'home.html', {'products': products})


def about(request):
    return render(request, 'about.html', {})


def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Do some shopping cart stuff here:
            current_user = Profile.objects.get(user__id=request.user.id)

            # Get their saved cart from database:
            # 'old_cart' is got from the Profile model that is imported and used above and named as the current_user, which is used here as well.
            # Remember that this 'old_cart' has been converted to a string in 'cart_add' function of the Cart class in 'Cart.py' file.
            saved_cart = current_user.old_cart

            # Convert Database string(current user's Profile that has the updated old_cart, that is: the saved_cart) to python dictionary:
            if saved_cart:
                # Convert from string to dictionary using JSON:
                converted_cart = json.loads(saved_cart)

                # Add the loaded cart dictionary to our session:
                # Get the cart:
                cart = Cart(request)

                #Loop through the cart and add the items from the database:
                # When you loop through a dictionary in python you have to call the '.items' function
                for key, value in converted_cart.items():
                    cart.db_add(product=key, quantity=value)


            messages.success(request, ("You Have Been Logged In!"))
            return redirect('home')
        else:
            messages.success(request, ("There was an error, please try again..."))
            return redirect('login')
    else:
        return render(request, 'login.html', {})
    

def logout_user(request):
    logout(request)
    messages.success(request, ("You have been logged out...Thanks for stopping by"))
    return redirect('home')


def register_user(request):
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            #log in user
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, ("Username Created - Please Fill Out Your User Info Below..."))
            return redirect('update_info')
        else:
            messages.success(request, ("Whoops! There was a problem Registering, please try again..."))
            return redirect('register')
    else:
        return render(request, 'register.html', {'form': form}) 

