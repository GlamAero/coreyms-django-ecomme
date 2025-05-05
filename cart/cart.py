from store.models import Product, Profile


class Cart():
    def __init__(self, request):

        # 'request.session' is a dictionary-like object that stores data for the current session. It is used to store and retrieve data that is specific to a user's session on the website. This dictionary-like object is created when a user accesses the website and is associated with a unique session ID.
        # 'request.session' is a way to persist data across multiple requests from the same user. It allows you to store information such as user preferences, shopping cart contents, and other session-specific data.
        self.session = request.session

        # Get request(for 'self.request.user'(currently logged in user)):
        self.request = request

        # Get the current session key if it exists
        # 'session_key' is a unique identifier for a session.
        # 'session_key' is a string that the Django session framework uses to track and associate session data with a specific client or user. This key is stored in the user's browser as a cookie and is also used on the server side to retrieve the associated session data.
        # 'session_key' is a pointer to 'django_session' which is a database table used to store session data. It store session data as key-value pairs. 
        # The 'session_key' is sent to the user's browser as a cookie (named 'sessionid' by default).
        # 'session_key' is the cart key used to create/store the cart in the session. 
        # And this session_key is in a dictionary format of key-value pairs (just as self.cart=cart below:).
        cart = self.session.get('session_key')

        # If the user is new, no session key! Create one!
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}

        # Make sure cart is available on all pages of site
        # self.cart(being cart = self.session['session_key']) is a dictionary that will hold the product id as the key and the quantity as the value
        # self.cart being cart is a dictionary of key=product id and value=quantity
        self.cart = cart

    # This 'db_add' function is for the database to ensure that cart items is added and 'remains' in the cart even after logging out and logging in. It displays it all out to be seen in the frontend:
    def db_add(self, product, quantity):
        product_id = str(product)  # make sure this is always string value since it is a string value in the dictionary
        product_qty = str(quantity) # this will be reconverted to integer down this code.

        # if product is already in cart:
        if product_id in self.cart:
            pass
        
        # If product is not in cart, add it: 
        else:
            # In the self.cart, being a dictionary will assign the product_id as the key and the quantity as the value:
            self.cart[product_id] = int(product_qty)  # make sure this is always converted to int value since it is an integer value in the dictionary

        # Saving the session:
        self.session.modified = True

        # Deal with logged in users and keep the cart content even after logging out: first, we update to the database and it remains there in the database even after logging out without the cart data being lost:
        if self.request.user.is_authenticated:
            # Get the current user profile using the Profile model because the Profile model contains the field: old_cart which is required here:
            current_user = Profile.objects.filter(user__id=self.request.user.id)

            # Convert the 'self.cart' which is a 'dictionary' having the product_id with double quotes(""), to 'string' having the product_id with single quote (''):
            carty = str(self.cart)

            # then replace the single quote(of the string) to double quote(even as a string). 
            # The quotes come after '\' to avoid errors. 
            # This is done because product_id come with "" and not '' in the default 'self.cart' dictionary:
            carty = carty.replace("\'", "\"")

            # Save the carty to the Profile Model:
            # 'old_cart' is a field in the Profile model in store app that stores the cart data as a string:
            current_user.update(old_cart=str(carty))


    
    # This 'add' function is used to add a new product to the cart without necessarily keeping the user's items in the cart after logging out and logging in
    def add(self, product, quantity):
        product_id = str(product.id)  # make sure this is always string value since it is a string value in the dictionary
        product_qty = str(quantity) # this will be reconverted to integer down this code.

        # if product is already in cart:
        if product_id in self.cart:
            pass
        
        # If product is not in cart, add it: 
        else:
            # In the self.cart, being a dictionary will assign the product_id as the key and the quantity as the value:
            self.cart[product_id] = int(product_qty)  # make sure this is always converted to int value since it is an integer value in the dictionary

        # Saving the session:
        self.session.modified = True

        # Deal with logged in users and keep the cart content even after logging out: first, we update to the database and it remains there in the database even after logging out without the cart data being lost:
        if self.request.user.is_authenticated:
            # Get the current user profile using the Profile model because the Profile model contains the field: old_cart which is required here:
            current_user = Profile.objects.filter(user__id=self.request.user.id)

            # Convert the 'self.cart' which is a 'dictionary' having the product_id with double quotes(""), to 'string' having the product_id with single quote (''):
            carty = str(self.cart)

            # then replace the single quote(of the string) to double quote(even as a string). 
            # The quotes come after '\' to avoid errors. 
            # This is done because product_id come with "" and not '' in the default 'self.cart' dictionary:
            carty = carty.replace("\'", "\"")

            # Save the carty to the Profile Model:
            # 'old_cart' is a field in the Profile Model
            current_user.update(old_cart=str(carty))

    
    def cart_total(self):
        # Get product IDs:
        # self.cart.keys() is a list of product ids in the cart:
        product_ids = self.cart.keys()

        # Look up those keys in our product database model:
        # 'Product.objects.filter(id__in=product_ids)' means that we are looking for all the products whose id is in the list of product_ids:
        products = Product.objects.filter(id__in=product_ids)

        # Get quantities:
        # 'self.cart' here is dictionary of 'key'(= the id of the quantity) and 'value'(= the quantity of the product) pairs
        quantities = self.cart

        # Start counting at 0:
        total = 0

        # 'quantities.items()' means that we are looping through a dictionary:
        # Loop through the dictionary and get the key and value:
        # By default the key being the product_id is a string(with "") and the value being the quantity is an integer:
        for key, value in quantities.items():
            # Convert key to integer value so we can do some maths:
            key = int(key)
            for product in products:
                if product.id == key:
                    if product.sale_price:
                        total = total + (product.sale_price * value) #value here is the real quantity selected by the user
                    else:
                        total = total + (product.price * value) # value here is the real quantity selected by the user

        return total


    # To get the quantity of the product in the cart:
    def __len__(self):
        return len(self.cart)
    
    
    # To see the content/product of the cart:
    def get_prods(self):
        # Get ids from cart:
        # ids = keys of products in the cart
        product_ids = self.cart.keys()

        # Filter out all products whose ids are in 'product_ids' from the database:(Remember that each product has a unique id):
        products = Product.objects.filter(id__in=product_ids)

        return products
    

    def get_quants(self):
        quantities = self.cart # 'self.cart' is the dictionary of {'product id': quantity} where 'product id' is a string and 'quantity' is an integer
        return quantities
    

    def update(self, product, quantity):
        product_id = str(product)  # make sure this is always string value since it is a string value in the dictionary
        product_qty = int(quantity)  # make sure this is always int value since it is an integer value in the dictionary

        # Get Cart
        ourcart = self.cart

        # Update the quantity of the particular product in the cart:
        # Update the quantity by assigning the newly selected quantity to the given product_id in the cart:
        ourcart[product_id] = product_qty 

        self.session.modified = True

        # Deal with logged in users and keep the cart content even after logging out: first, we update to the database and it remains there in the database even after logging out without the cart data being lost:
        if self.request.user.is_authenticated:
            # Get the current user profile using the Profile model because the Profile model contains the field: old_cart which is required here:
            current_user = Profile.objects.filter(user__id=self.request.user.id)

            # Convert the 'self.cart' which is a 'dictionary' having the product_id with double quotes(""), to 'string' having the product_id with single quote (''):
            carty = str(self.cart)

            # then replace the single quote(of the string) to double quote(even as a string). 
            # The quotes come after '\' to avoid errors. 
            # This is done because product_id come with "" and not '' in the default 'self.cart' dictionary:
            carty = carty.replace("\'", "\"")

            # Save the carty to the Profile Model:
            current_user.update(old_cart=str(carty))

        thing = self.cart  # the updated cart
        return thing
    

    def delete(self, product):
        product_id = str(product)  # make sure this is always string value since it is a string value in the dictionary

        if product_id in self.cart:
            del self.cart[product_id]

        self.session.modified = True

        # Deal with logged in users and keep the cart content even after logging out: first, we update to the database and it remains there in the database even after logging out without the cart data being lost:
        if self.request.user.is_authenticated:
            # Get the current user profile using the Profile model because the Profile model contains the field: old_cart which is required here:
            current_user = Profile.objects.filter(user__id=self.request.user.id)

            # Convert the 'self.cart' which is a 'dictionary' having the product_id with double quotes(""), to 'string' having the product_id with single quote (''):
            carty = str(self.cart)

            # then replace the single quote(of the string) to double quote(even as a string). 
            # The quotes come after '\' to avoid errors. 
            # This is done because product_id come with "" and not '' in the default 'self.cart' dictionary:
            carty = carty.replace("\'", "\"")

            # Save the carty to the Profile Model:
            current_user.update(old_cart=str(carty))
        

