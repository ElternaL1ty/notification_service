# Generated by Django 3.2.5 on 2022-04-07 12:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification_app', '0003_auto_20220407_1435'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='phone',
            field=models.CharField(max_length=11),
        ),
        migrations.AlterField(
            model_name='client',
            name='utc',
            field=models.CharField(max_length=6),
        ),
    ]