from django.db import models
from django.contrib.auth.models import User
from store.models import Product
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
import datetime

# Create your models here.
class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null= True, blank = True)
    shipping_full_name = models.CharField(max_length=255)
    shipping_email = models.EmailField(max_length=255)
    shipping_address1 = models.CharField(max_length=255)
    shipping_address2 = models.CharField(max_length=255, null=True, blank=True)
    shipping_city = models.CharField(max_length=255)
    shipping_state = models.CharField(max_length=255, null=True, blank=True)
    shipping_zipcode = models.CharField(max_length=255, null=True, blank=True)
    shipping_country = models.CharField(max_length=255)

    # Don't pluralize address
    class Meta:
        verbose_name_plural = 'Shipping Address'

    def __str__(self):
        return f'Shipping Address - {str(self.id)}'
    

# To automatically create a Shipping Address for a user when they sign up:
# Create a user Shipping Address by default when user signs up:
# This Shipping Address is a form containing fields to be filled by the signed  up user
def create_shipping(sender, instance, created, **kwargs):
    
    # In the below, 'if created' is used to check whether a new user instance('user instance' is the user detail at sign up) has been created.
    # In other words, 'if created' checks whether the user has signed up or not.
    if created:
        # in the below, 'instance' here refers to the particular user who filled all the fields of the Shipping address at the time of registering/signing up.
        # This instance user has in it fields like 'username', 'email', 'password' and other fields that are in the User model.
        # Thus here we are getting the Shipping address(given by all the field of the ShippingAddress model) of the user who just signed up and creating a ShippingAddress object for that user.
        # This means; 'ShippingAddress(user=instance)' is creating a new ShippingAddress object and associating it with the user instance. It is like saying "this shipping address belongs to this user". However, it does not save it to the database yet until 'user_shipping.save()' is called. And user_saving.save() is only called after the user has filled all the fields of the ShippingAddress model as in the ShippingForm that appears.
        user_shipping = ShippingAddress(user=instance)
        user_shipping.save()

# Automate the shipping thing:
# 'post_save' is a signal that is sent after a model's save() method is called. It is used to perform actions after an object has been saved to the database.
post_save.connect(create_shipping, sender=User)

    

# Create Order Model:
class Order(models.Model):
    # Foreign Key:
    # 'null = True' and 'blank=True' because the a guest who did not sign in as a user can make an order and checkout
    user = models.ForeignKey(User, on_delete=models.CASCADE, null= True, blank=True)
    full_name = models.CharField(max_length=250)
    email = models.EmailField(max_length=250)

    # 'shipping_address' would contain the address, city, state, zipcode, country and possibly other details
    shipping_address = models.TextField(max_length=15000)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    date_ordered = models.DateTimeField(auto_now_add=True)
    shipped = models.BooleanField(default=False)
    date_shipped = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f'Order - {str(self.id)}'
    

# Automatically Add Shipping Date when Order is Shipped:q
# Here, we are using the 'pre_save' signal to 'automatically' set the 'date_shipped' field to the current date and time when the order is shipped. It prompts to get the current date and time when the order is shipped; that is it gets the date and time when the 'shipped' field is set to True.
# The 'pre_save' signal is sent just before the model's 'save()' method is called.
# this function is created to make sure that the 'date_shipped' field is set to the current date and time when the order is shipped:
@receiver(pre_save, sender=Order)
def set_shipped_date_on_update(sender, instance, **kwargs):

    # 'instance' here refers to the current instance of the Order model that is being saved.
    # In other words, 'instance' is the current order that is being processed or updated.
    # 'instance.pk' is commonly used to check whether the current instance of the model(Order) has already been saved in the database:
    if instance.pk:
        now = datetime.datetime.now()

        # Check if the order is shipped and update the date_shipped field
        # 'sender.default_manager.get(pk=instance.pk)' is typically used in signals to retrieve the updated or current version of an instance directly from the database: 
        # 'default_manager' is the default manager for the model. In Django, every model class has a manager.
        # 'default_manager' is responsible for database operations like querying or creating instances
        # sender: the model class (Order) that the signal is connected to that triggered the signal. Remember that 'sender=Order' is the model class that the signal is connected to.
        # instance: the instance of the model that is being saved (the order being updated)
        # '.get(pk=instance.pk)' retrieves the current version of the instance(Order) from the database using its primary key- (pk).
        # 'instance.pk' is the primary key of the instance being saved. It is used to identify the specific record in the database.
        # Using 'instance.pk' ensures you're retrieving the exact database version of the instance, not the version in memory. In other words, 'instance.pk' is used to get the current order from the database.
        # This therefore means, 'obj' is the default(old/existing) version value of the Order model in the database.
        obj = sender._default_manager.get(pk=instance.pk)


        # 'instance.shipped' is the new value of the 'shipped' field that is being saved.
        # 'obj.shipped' is the previous/default value of the 'shipped' field in the database which is set to 'False' in the database.
        # The below then means, if the current version of the order instance being saved has 'shipped' set to True and the previous version of the order instance in the database has 'shipped' set to False, then set the 'date_shipped' field to the current date and time.
        # In other words, if the order is being shipped (shipped=True) and the default value of shipped being 'False' is no longer False but True, set the date_shipped to the value of 'now'.
        if instance.shipped and not obj.shipped:
            instance.date_shipped = now


# Create Order Items Model:
class OrderItem(models.Model):
    # Foreign keys
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null= True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null= True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null= True, blank=True)
    quantity = models.PositiveBigIntegerField(default=1)
    price = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        return f'Order Item - {str(self.id)}'

