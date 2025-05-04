import os
from datetime import datetime


def rental_item_storage(instance, filename):
    rental_item_id = instance.id
    if rental_item_id is None:
        rental_item_id = "new"
    ext = filename.split(".")[-1]
    new_filename = f"rental_item_{rental_item_id}_image.{ext}"
    return os.path.join("rental_item/images/", new_filename)


def item_set_storage(instance, filename):
    item_set_id = instance.id
    if item_set_id is None:
        item_set_id = "new"
    ext = filename.split(".")[-1]
    new_filename = f"item_set_{item_set_id}_image.{ext}"
    return os.path.join("item_set/images/", new_filename)


def payment_slip_storage(instance, filename):
    payment_slip_id = instance.id
    if payment_slip_id is None:
        payment_slip_id = "new"
    ext = filename.split(".")[-1]
    new_filename = f"payment_slip_{payment_slip_id}_image_{datetime.now()}.{ext}"
    return os.path.join("payment_slip/images/", new_filename)
