# Generated by Django 3.2.9 on 2021-12-18 18:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('farmapp', '0012_orders_order_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='orders',
            name='buyer_delivered',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='orders',
            name='seller_delivered',
            field=models.BooleanField(default=False),
        ),
    ]
