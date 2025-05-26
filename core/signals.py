import uuid

from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone

from core.models import ItemSet, RentalItem


@receiver(pre_save, sender=RentalItem)
def generate_serial_number(sender, instance, **kwargs):
    if not instance.serial_number:
        prefix = "RI"
        date_str = timezone.now().strftime("%Y%m%d")
        sequence = str(uuid.uuid4().int)[-3:]
        instance.serial_number = f"{prefix}-{date_str}-{sequence}"
        print("Signals: generate serial number.")


@receiver(pre_save, sender=RentalItem)
def handle_item_image_on_update(sender, instance, **kwargs):
    if not instance.image:
        return

    image_changed = False

    if instance.pk:
        try:
            old_instance = sender.objects.only("image").get(pk=instance.pk)
            image_changed = old_instance.image != instance.image
            if image_changed and old_instance.image:
                old_instance.image.delete(save=False)
                print("Signals: update rental item image.")
        except sender.DoesNotExist:
            pass  # Old instance does not exist, this must be a new instance


@receiver(pre_delete, sender=RentalItem)
def delete_item_image_on_delete(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete(save=False)
        print("Signals: delete rental item image.")


@receiver(pre_save, sender=ItemSet)
def handle_item_set_image_on_update(sender, instance, **kwargs):
    if not instance.image:
        return

    image_changed = False

    if instance.pk:
        try:
            old_instance = sender.objects.only("image").get(pk=instance.pk)
            image_changed = old_instance.image != instance.image
            if image_changed and old_instance.image:
                old_instance.image.delete(save=False)
                print("Signals: update item set image.")
        except sender.DoesNotExist:
            pass  # Old instance does not exist, this must be a new instance


@receiver(pre_delete, sender=ItemSet)
def delete_item_set_image_on_delete(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete(save=False)
        print("Signals: delete item set image.")
