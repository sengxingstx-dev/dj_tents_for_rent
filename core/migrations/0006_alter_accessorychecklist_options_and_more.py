# Generated by Django 4.2.15 on 2025-05-02 16:10

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models

import core.utils


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0005_alter_rentalitemtype_type_name"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="accessorychecklist",
            options={"ordering": ["accessory__accessory_name"]},
        ),
        migrations.AlterModelOptions(
            name="damagereport",
            options={"ordering": ["-damage_date"]},
        ),
        migrations.AlterModelOptions(
            name="payment",
            options={"ordering": ["-transaction_date"]},
        ),
        migrations.AlterModelOptions(
            name="rentalitem",
            options={"ordering": ["item_type", "serial_number"]},
        ),
        migrations.AlterModelOptions(
            name="rentalitemdetail",
            options={"ordering": ["item__item_type", "item__serial_number"]},
        ),
        migrations.AlterModelOptions(
            name="rentalitemtype",
            options={"ordering": ["type_name"]},
        ),
        migrations.AlterModelOptions(
            name="rentalsetdetail",
            options={"ordering": ["item_set__name"]},
        ),
        migrations.AlterModelOptions(
            name="rentaltransaction",
            options={"ordering": ["-start_date", "-created_at"]},
        ),
        migrations.RenameField(
            model_name="damagereport",
            old_name="checklist",
            new_name="accessory_checklist",
        ),
        migrations.RemoveField(
            model_name="damagereport",
            name="paid_status",
        ),
        migrations.RemoveField(
            model_name="damagereport",
            name="quantity_damaged",
        ),
        migrations.RemoveField(
            model_name="maintenancerecord",
            name="accessory",
        ),
        migrations.RemoveField(
            model_name="payment",
            name="damage",
        ),
        migrations.RemoveField(
            model_name="rentaltransaction",
            name="sets",
        ),
        migrations.AddField(
            model_name="accessorychecklist",
            name="notes",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="accessorychecklist",
            name="quantity_expected",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="damagereport",
            name="rental_detail",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="damage_reports",
                to="core.rentalitemdetail",
            ),
        ),
        migrations.AddField(
            model_name="itemset",
            name="image",
            field=models.ImageField(blank=True, null=True, upload_to=core.utils.item_set_storage),
        ),
        migrations.AddField(
            model_name="payment",
            name="damage_fine_paid",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="payments",
                to="core.damagereport",
            ),
        ),
        migrations.AddField(
            model_name="rentalitemdetail",
            name="item",
            field=models.ForeignKey(
                default=1, on_delete=django.db.models.deletion.CASCADE, to="core.rentalitem"
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="payment",
            name="payment_method",
            field=models.CharField(
                choices=[
                    ("cash", "Cash"),
                    ("bank_transfer", "Bank Transfer"),
                    ("credit_card", "Credit Card"),
                ],
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="rentalitemtype",
            name="type_name",
            field=models.CharField(
                choices=[
                    ("tent", "Tent"),
                    ("table", "Table"),
                    ("chair", "Chair"),
                    ("fan", "Fan"),
                    ("tablecloth", "Tablecloth"),
                    ("other", "Other"),
                ],
                max_length=50,
            ),
        ),
        migrations.AlterField(
            model_name="rentaltransaction",
            name="payment_status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("paid", "Paid"),
                    ("partial", "Partial"),
                    ("cancelled", "Cancelled"),
                    ("refunded", "Refunded"),
                ],
                default="pending",
                max_length=20,
            ),
        ),
        migrations.AlterUniqueTogether(
            name="accessorychecklist",
            unique_together={("rental_detail", "accessory")},
        ),
        migrations.AlterUniqueTogether(
            name="rentalitemdetail",
            unique_together={("rental", "item")},
        ),
        migrations.AlterUniqueTogether(
            name="rentalsetdetail",
            unique_together={("rental", "item_set")},
        ),
    ]
