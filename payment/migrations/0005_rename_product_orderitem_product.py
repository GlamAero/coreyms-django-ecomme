# Generated by Django 5.1.7 on 2025-04-07 14:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0004_alter_shippingaddress_shipping_address2_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orderitem',
            old_name='Product',
            new_name='product',
        ),
    ]
