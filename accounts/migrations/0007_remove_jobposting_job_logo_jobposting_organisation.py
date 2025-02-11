# Generated by Django 5.1.5 on 2025-02-04 08:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_alter_jobseekerprofile_experience_years_jobposting'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='jobposting',
            name='job_logo',
        ),
        migrations.AddField(
            model_name='jobposting',
            name='organisation',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='job_postings', to='accounts.organisationregister'),
            preserve_default=False,
        ),
    ]
