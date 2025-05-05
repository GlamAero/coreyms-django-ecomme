from django.contrib import admin
from .models import ShippingAddress, Order, OrderItem
from django.contrib.auth.models import User


# Register your models here.
admin.site.register(ShippingAddress)
admin.site.register(Order)
admin.site.register(OrderItem)


# Create an OrderItem Inline:
class OrderItemInline(admin.StackedInline):
    model = OrderItem
    # without specifying 'extra', the default value is 3, so it will show 3 empty OrderItem forms in the admin panel
    # 'extra' is the number of empty forms to show in the admin panel:
    # so '
    # so extra' is set to 0, so it won't show any empty OrderItem form in the admin panel
    # so it will only show the OrderItem forms that are already in the database:
    extra = 0


# Extend our Order model to include the OrderItemInline:
class OrderAdmin(admin.ModelAdmin):
    model = Order
    # Ordinarily, the readonly_fields would not be displayed in the admin panel but we can make it appear by calling the 'readonly_fields' here.
    # 'readonly_fields' is a list of fields that will be displayed as read-only in the admin panel:
    # so the 'date_ordered' field will be displayed as read-only(without the capacity to edit it) in the admin panel:
    readonly_fields = ["date_ordered"]
    fields = ["user", "full_name", "email", "shipping_address", "amount_paid", "date_ordered", "shipped", "date_shipped"]
    inlines = [OrderItemInline]


# Unregister the default Order model:
admin.site.unregister(Order)


# Register the new Order model with the OrderItemInline:
admin.site.register(Order, OrderAdmin)
