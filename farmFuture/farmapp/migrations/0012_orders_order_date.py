# Generated by Django 3.2.9 on 2021-12-15 17:35

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('farmapp', '0011_auto_20211215_1728'),
    ]

    operations = [
        migrations.AddField(
            model_name='orders',
            name='order_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
