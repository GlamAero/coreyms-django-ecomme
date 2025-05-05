from django.contrib import admin
from .models import Category, Customer, Product, Order, Profile
from django.contrib.auth.models import User

# Register your models here:
admin.site.register(Category)
admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Profile)


# Here we are adding more features to the user profile that is we are adding a new page('Update Info') is now created for that::

# Mix Profile info and user info:
class ProfileInline(admin.StackedInline):
    model = Profile


# Extend User Model:
class UserAdmin(admin.ModelAdmin):
    model = User
    fields = ['username', 'first_name', 'last_name', 'email']

    # 'inlines' is used to add the other content of the Profile model to the admin interface.
    inlines = [ProfileInline]


# Unregister the old way here:
admin.site.unregister(User)

# Re-register the new way:
admin.site.register(User, UserAdmin)
