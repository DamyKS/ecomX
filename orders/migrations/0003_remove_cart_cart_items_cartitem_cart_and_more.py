# Generated by Django 5.1.6 on 2025-03-11 20:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_remove_cartitem_cart_cart_cart_items_cart_status_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='cart_items',
        ),
        migrations.AddField(
            model_name='cartitem',
            name='cart',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='orders.cart'),
        ),
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_address',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
    ]
