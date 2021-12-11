# Generated by Django 3.2.9 on 2021-12-11 20:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('farmapp', '0002_auto_20211211_1650'),
    ]

    operations = [
        migrations.AddField(
            model_name='webuser',
            name='aadhaar_link',
            field=models.URLField(default=''),
        ),
        migrations.AddField(
            model_name='webuser',
            name='farmer_id',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AddField(
            model_name='webuser',
            name='request_farmer',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='webuser',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.group'),
        ),
    ]
