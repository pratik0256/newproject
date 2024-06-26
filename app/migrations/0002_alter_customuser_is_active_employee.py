# Generated by Django 5.0.3 on 2024-04-09 07:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="is_active",
            field=models.BooleanField(blank=True, default=None, null=True),
        ),
        migrations.CreateModel(
            name="Employee",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("check_in", models.DateTimeField(blank=True, null=True)),
                ("check_out", models.DateTimeField(blank=True, null=True)),
                ("is_active", models.BooleanField(blank=True, default=None, null=True)),
                ("is_working_from_home", models.BooleanField(default=False)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="employee_profile",
                        to="app.customuser",
                    ),
                ),
            ],
        ),
    ]
