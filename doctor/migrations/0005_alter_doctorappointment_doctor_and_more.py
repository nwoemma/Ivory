# Generated by Django 5.0.7 on 2024-08-09 22:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("doctor", "0004_alter_doctorappointment_doctor_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="doctorappointment",
            name="doctor",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="doctor_appointments_set",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="doctorappointment",
            name="patient",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="patient_appointments_set",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
