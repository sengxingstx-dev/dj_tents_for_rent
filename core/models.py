import decimal

from django.db import models
from django.db.models import Count, F, Sum
from django.urls import reverse

from accounts.models import Account, Customer
from common.models import BaseModel
from core.utils import item_set_storage, payment_slip_storage, rental_item_storage


class ItemStatus(models.TextChoices):
    AVAILABLE = "available", "Available"
    UNDER_MAINTENANCE = "under_maintenance", "Under Maintenance"
    RETIRED = "retired", "Retired"


class ItemType(models.TextChoices):
    TENT = "tent", "Tent"
    TABLE = "table", "Table"
    CHAIR = "chair", "Chair"
    FAN = "fan", "Fan"
    TABLECLOTH = "tablecloth", "Tablecloth"
    other = "other", "Other"


class DamageStatus(models.TextChoices):
    REPORTED = "reported", "Reported"
    CONFIRMED = "confirmed", "Confirmed"
    REPAIRED = "repaired", "Repaired"
    CHARGED = "charged", "Charged"


class PaymentType(models.TextChoices):
    DEPOSIT = "deposit", "Deposit"
    RENTAL_FEE = "rental_fee", "Rental Fee"
    DAMAGE_FINE = "damage_fine", "Damage Fine"
    OTHER = "other", "Other"


class MaintenanceType(models.TextChoices):
    ROUTINE = "routine", "Routine"
    REPAIR = "repair", "Repair"
    REPLACEMENT = "replacement", "Replacement"
    CLEANING = "cleaning", "Cleaning"


class PaymentStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PAID = "paid", "Paid"
    PARTIAL = "partial", "Partial"
    CANCELLED = "cancelled", "Cancelled"
    REFUNDED = "refunded", "Refunded"


class MaintenanceStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    COMPLETED = "completed", "Completed"
    IN_PROGRESS = "in_progress", "In Progress"


class PaymentMethod(models.TextChoices):
    BANK_TRANSFER = "bank_transfer", "Bank Transfer"
    CASH = "cash", "Cash"
    CREDIT_CARD = "credit_card", "Credit Card"


class RentalItemType(BaseModel):
    type_name = models.CharField(max_length=50, choices=ItemType.choices)
    description = models.TextField(blank=True)
    size = models.CharField(max_length=50, blank=True)
    capacity = models.IntegerField(blank=True, null=True)
    rental_price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    replacement_cost = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["type_name"]  # Add default ordering

    def __str__(self):
        return self.get_type_name_display()


class RentalItem(BaseModel):
    item_type = models.ForeignKey(RentalItemType, on_delete=models.CASCADE)
    serial_number = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to=rental_item_storage, null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=ItemStatus.choices, default=ItemStatus.AVAILABLE
    )
    purchase_date = models.DateField(blank=True, null=True)
    last_inspection_date = models.DateField(blank=True, null=True)
    condition_notes = models.TextField(blank=True)

    class Meta:
        ordering = ["item_type", "serial_number"]

    def __str__(self):
        return f"{self.item_type} - {self.serial_number}"

    def get_absolute_url(self):
        # Useful for linking directly to an item's detail page (if you create one)
        # return reverse('item_detail', kwargs={'pk': self.pk})
        # Or if you don't have a specific detail page, maybe link to home or category
        return reverse("home")  # Placeholder


class ItemSet(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    replacement_deposit = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to=item_set_storage, null=True, blank=True)

    def __str__(self):
        return f"{self.name}"

    @property
    def total_component_price_per_day(self):
        """Calculate the sum of individual component prices per day."""
        total = decimal.Decimal("0.00")
        for component in self.itemsetcomponent_set.select_related("item_type").all():
            total += component.item_type.rental_price_per_day * component.quantity
        return total

    @property
    def available_quantity(self):
        """
        Calculate how many complete sets are currently available based on
        the availability of their components.
        This performs database queries, use with caution in loops or list views.
        Consider caching this value if performance becomes an issue.
        """
        components = self.itemsetcomponent_set.select_related("item_type").all()
        if not components.exists():
            return 0

        # Use aggregation for potentially better performance than looping N times
        component_types = components.values_list("item_type_id", "quantity")
        type_ids = [ct[0] for ct in component_types]

        # Get counts of available items for all relevant types in one query
        available_item_counts = (
            RentalItem.objects.filter(item_type_id__in=type_ids, status=ItemStatus.AVAILABLE)
            .values("item_type_id")
            .annotate(count=Count("id"))
        )

        # Create a dictionary for easy lookup: {item_type_id: available_count}
        available_map = {item["item_type_id"]: item["count"] for item in available_item_counts}

        min_possible_sets = float("inf")  # Start with infinity

        for item_type_id, required_quantity in component_types:
            available_count = available_map.get(item_type_id, 0)
            if required_quantity == 0:  # Avoid division by zero if quantity is somehow 0
                continue
            possible_sets_for_component = available_count // required_quantity
            min_possible_sets = min(min_possible_sets, possible_sets_for_component)

        # If min_possible_sets is still infinity, it means a component type was missing entirely
        return int(min_possible_sets) if min_possible_sets != float("inf") else 0

    def get_absolute_url(self):
        # Example: URL to view the set details or add it to selection
        # return reverse('set_detail', kwargs={'pk': self.pk})
        return reverse("home")  # Placeholder


class ItemSetComponent(BaseModel):
    item_set = models.ForeignKey(ItemSet, on_delete=models.CASCADE)
    item_type = models.ForeignKey(RentalItemType, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("item_set", "item_type")  # Ensures one entry per type per set

    def __str__(self):
        return f"{self.item_set.name} - {self.quantity} x {self.item_type}"


class RentalTransaction(BaseModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    total_deposit = models.DecimalField(max_digits=10, decimal_places=2)
    total_fines = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(
        max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING
    )

    class Meta:
        ordering = ["-start_date", "-created_at"]  # Order by start date descending

    def __str__(self):
        return f"Rental #{self.id} - {self.customer}"

    @property
    def total_rental_days(self):
        """Calculate rental duration in days (inclusive)."""
        if self.start_date and self.end_date:
            return max(1, (self.end_date - self.start_date).days + 1)
        return 0

    @property
    def total_rental_cost(self):
        """Calculate the total cost based on rented details and duration."""
        total_cost = decimal.Decimal("0.00")
        duration = self.total_rental_days

        # Sum cost from individual items
        item_cost = self.rentalitemdetail_set.filter(set_rental__isnull=True).aggregate(
            total=Sum(F("quantity") * F("rented_price_per_day"))
        )["total"] or decimal.Decimal("0.00")
        total_cost += item_cost

        # Sum cost from sets
        set_cost = self.rentalsetdetail_set.aggregate(
            total=Sum(F("quantity") * F("rented_price_per_day"))
        )["total"] or decimal.Decimal("0.00")
        total_cost += set_cost

        return total_cost * duration

    @property
    def amount_paid(self):
        """Calculate the total amount paid for this rental (excluding cancelled/refunded)."""
        return self.payment_set.filter(
            rental=self,
            # Exclude potentially reversed payments if needed
            # payment_type__in=[PaymentType.DEPOSIT, PaymentType.RENTAL_FEE, PaymentType.DAMAGE_FINE]
        ).aggregate(total=Sum("amount"))["total"] or decimal.Decimal("0.00")

    @property
    def balance_due(self):
        """Calculate the remaining balance."""
        # This is a simplified balance; real calculation might depend on payment types, fines, etc.
        return (self.total_rental_cost + self.total_fines) - self.amount_paid


class RentalSetDetail(BaseModel):
    rental = models.ForeignKey(RentalTransaction, on_delete=models.CASCADE)
    item_set = models.ForeignKey(ItemSet, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    rented_price_per_day = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        # Ensure a transaction doesn't rent the same set twice (use quantity instead)
        unique_together = ("rental", "item_set")
        ordering = ["item_set__name"]

    def __str__(self):
        return f"Rental #{self.rental.id} - {self.quantity} x {self.item_set.name}"


class RentalItemDetail(BaseModel):
    rental = models.ForeignKey(RentalTransaction, on_delete=models.CASCADE)
    item = models.ForeignKey(RentalItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    rented_price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    set_rental = models.ForeignKey(
        RentalSetDetail, on_delete=models.SET_NULL, null=True, blank=True, related_name="components"
    )

    class Meta:
        # Ensure a transaction doesn't link the same specific item twice
        unique_together = ("rental", "item")
        ordering = ["item__item_type", "item__serial_number"]

    def __str__(self):
        if self.set_rental:
            return f"Rental #{self.rental.id} - {self.item} (Part of Set: {self.set_rental.item_set.name})"
        else:
            return f"Rental #{self.rental.id} - {self.item} (Individual)"


class Accessory(BaseModel):
    item_type = models.ForeignKey(RentalItemType, on_delete=models.CASCADE)
    accessory_name = models.CharField(max_length=100)
    standard_quantity = models.IntegerField(default=1)
    replacement_cost = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.accessory_name}"


class AccessoryChecklist(BaseModel):
    rental_detail = models.ForeignKey(RentalItemDetail, on_delete=models.CASCADE)
    accessory = models.ForeignKey(Accessory, on_delete=models.CASCADE)
    quantity_expected = models.IntegerField(default=0)
    quantity_checked = models.IntegerField()
    quantity_returned = models.IntegerField(blank=True, null=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = (
            "rental_detail",
            "accessory",
        )  # One checklist entry per accessory per rented item detail
        ordering = ["accessory__accessory_name"]

    def __str__(self):
        return f"{self.accessory} Checklist"


class MaintenanceRecord(BaseModel):
    item = models.ForeignKey(RentalItem, on_delete=models.CASCADE, null=True, blank=True)
    maintenance_type = models.CharField(max_length=20, choices=MaintenanceType.choices)
    start_date = models.DateField()
    completion_date = models.DateField(blank=True, null=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    technician = models.CharField(max_length=100, blank=True)
    status = models.CharField(
        max_length=20, choices=MaintenanceStatus.choices, default=MaintenanceStatus.PENDING
    )

    def __str__(self):
        item_str = f"Item {self.item}" if self.item else "General Maintenance"
        return f"Maintenance #{self.id} ({item_str}) - {self.get_maintenance_type_display()}"


class DamageReport(BaseModel):
    rental_detail = models.ForeignKey(
        RentalItemDetail,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="damage_reports",
    )
    accessory_checklist = models.ForeignKey(AccessoryChecklist, on_delete=models.CASCADE)
    maintenance = models.ForeignKey(
        MaintenanceRecord, on_delete=models.SET_NULL, null=True, blank=True
    )
    reported_by = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True)
    damage_description = models.TextField()
    damage_date = models.DateField()
    damage_status = models.CharField(
        max_length=20, choices=DamageStatus.choices, default=DamageStatus.REPORTED
    )
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["-damage_date"]

    def __str__(self):
        target = "Unknown Item"
        if self.rental_detail and self.rental_detail.item:
            target = str(self.rental_detail.item)
        elif self.accessory_checklist and self.accessory_checklist.accessory:
            target = str(self.accessory_checklist.accessory)
        return f"Damage Report #{self.id} ({target}) - {self.get_damage_status_display()}"


class Payment(BaseModel):
    rental = models.ForeignKey(RentalTransaction, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    payment_type = models.CharField(max_length=20, choices=PaymentType.choices)
    payment_slip = models.ImageField(upload_to=payment_slip_storage, null=True, blank=True)
    damage_fine_paid = models.ForeignKey(
        DamageReport, on_delete=models.SET_NULL, null=True, blank=True, related_name="payments"
    )
    transaction_date = models.DateTimeField(auto_now_add=True)
    reference_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-transaction_date"]

    def __str__(self):
        return f"Payment #{self.id} ({self.amount} via {self.get_payment_method_display()}) for Rental #{self.rental.id}"
