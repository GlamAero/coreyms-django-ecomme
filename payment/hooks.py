from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver
from django.conf import settings
import time
from .models import Order


# This function is called when a valid IPN message is received from PayPal to the website.
@receiver(valid_ipn_received)
def paypal_payment_received(sender, **kwargs):

    # Add a ten second pause to allow the IPN message to be processed(for paypal to send the IPN data):    
    time.sleep(10)

    # Grab the info that paypal sends to the website:
    paypal_obj = sender

    # Grab the paypal's invoice number from the IPN message:
    my_invoice = str(paypal_obj.invoice)
    
    # Match the order's invoice number in the database to paypal's invoice number to see if they match:
    my_Order = Order.objects.get(invoice=my_invoice)

    # Record the Order was paid:
    my_Order.paid = True

    # Save the order:
    my_Order.save()
