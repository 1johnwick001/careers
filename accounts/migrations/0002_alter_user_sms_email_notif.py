# Generated by Django 5.1.5 on 2025-01-27 05:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='sms_email_notif',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
