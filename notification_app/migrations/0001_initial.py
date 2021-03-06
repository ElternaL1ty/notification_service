# Generated by Django 3.2.5 on 2022-04-06 22:00

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('phone', models.CharField(max_length=11, validators=[django.core.validators.RegexValidator(message='Телефон должен быть введен в формате 7XXXXXXXXXX', regex='/^7[0-9]{10}/')])),
                ('operator_code', models.IntegerField()),
                ('tag', models.CharField(max_length=20)),
                ('utc', models.CharField(max_length=6, validators=[django.core.validators.RegexValidator(message='Часовой пояс вводится в формате UTC-X или UTC-XX', regex='/UTC[+?-][0-9]{1,2}/')])),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('start_datetime', models.DateTimeField()),
                ('end_datetime', models.DateTimeField()),
                ('message_text', models.TextField()),
                ('operator_code_filter', models.JSONField(blank=True, null=True)),
                ('tag_filter', models.JSONField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('sending_datetime', models.DateTimeField(auto_now=True)),
                ('sending_status', models.CharField(max_length=10)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='notification_app.client')),
                ('notification_id', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='notification_app.notification')),
            ],
        ),
    ]
