# Generated by Django 5.1.6 on 2025-03-12 02:10

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0003_remove_store_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='store',
            name='hero_image',
            field=cloudinary.models.CloudinaryField(max_length=255, null=True, verbose_name='stores/images'),
        ),
    ]
