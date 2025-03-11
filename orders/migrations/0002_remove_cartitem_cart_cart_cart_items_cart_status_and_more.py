# Generated by Django 5.1.6 on 2025-03-11 19:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
        ('products', '0001_initial'),
        ('stores', '0003_remove_store_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cartitem',
            name='cart',
        ),
        migrations.AddField(
            model_name='cart',
            name='cart_items',
            field=models.ManyToManyField(null=True, related_name='cart', to='orders.cartitem'),
        ),
        migrations.AddField(
            model_name='cart',
            name='status',
            field=models.CharField(default='active', max_length=20),
        ),
        migrations.AddField(
            model_name='order',
            name='cart',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='orders.cart'),
        ),
        migrations.AlterField(
            model_name='cartitem',
            name='product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='products.product'),
        ),
        migrations.AlterField(
            model_name='order',
            name='store',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='stores.store'),
        ),
    ]
