from django import forms
from django.utils import timezone

from accounts.models import Customer, Employee
from core.models import (
    Accessory,
    ItemSet,
    ItemSetComponent,
    PaymentMethod,
    RentalItem,
    RentalItemType,
)


# HOME / BOOKING SELECTION
class BookingForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-input mt-1 block w-full rounded-md border-gray-300 "
                "shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 "  # Adjusted focus ring color
                "focus:ring-opacity-50 dark:bg-gray-700 dark:border-gray-600 dark:text-white",
                "min": timezone.now().strftime(
                    "%Y-%m-%d"
                ),  # Prevent selecting past dates in browser
            }
        ),
        initial=timezone.now().date(),
        help_text="Select the start date for your rental.",
    )
    end_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-input mt-1 block w-full rounded-md border-gray-300 "
                "shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 "
                "focus:ring-opacity-50 dark:bg-gray-700 dark:border-gray-600 dark:text-white",
                "min": timezone.now().strftime("%Y-%m-%d"),  # Prevent selecting past dates
            }
        ),
        help_text="Select the end date for your rental.",
    )
    payment_method = forms.ChoiceField(
        choices=PaymentMethod.choices,
        widget=forms.Select(
            attrs={
                "class": "form-select mt-1 block w-full rounded-md border-gray-300 shadow-sm "
                "focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 "
                "dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            }
        ),
        help_text="Choose your preferred payment method for the deposit/fee.",
    )

    payment_slip = forms.ImageField(
        required=False,  # Make it optional initially, maybe required based on payment method later
        widget=forms.ClearableFileInput(
            attrs={
                "class": "form-input mt-1 block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400",
                "accept": "image/*",  # Suggest browser accept only images
            }
        ),
        help_text="Optional: Upload proof of payment (e.g., GCash screenshot).",
    )

    def clean_start_date(self):
        start_date = self.cleaned_data.get("start_date")
        if start_date and start_date < timezone.now().date():
            raise forms.ValidationError("Start date cannot be in the past.")
        return start_date

    def clean_end_date(self):
        start_date = self.cleaned_data.get("start_date")
        end_date = self.cleaned_data.get("end_date")

        if not end_date:  # Check if end_date is provided
            raise forms.ValidationError("End date is required.")

        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError("End date cannot be before the start date.")

        # Optional: Add validation for minimum/maximum rental duration
        if start_date and end_date:
            duration = (end_date - start_date).days + 1
            if duration < 1:  # Should be handled by previous check, but good practice
                raise forms.ValidationError("Minimum rental duration is 1 day.")
            max_duration = 30  # Example
            if duration > max_duration:
                raise forms.ValidationError(f"Maximum rental duration is {max_duration} days.")

        return end_date

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        # Ensure end_date validation runs even if start_date has errors
        if start_date and not end_date and "end_date" not in self._errors:
            self.add_error("end_date", "End date is required.")
        elif start_date and end_date and end_date < start_date and "end_date" not in self._errors:
            self.add_error("end_date", "End date cannot be before the start date.")

        # You might add validation here later, e.g., require payment_slip if method is 'Bank Transfer'
        payment_method = cleaned_data.get("payment_method")
        payment_slip = cleaned_data.get("payment_slip")
        if payment_method == PaymentMethod.BANK_TRANSFER and not payment_slip:
            self.add_error("payment_slip", "Payment slip is required for Bank Transfer.")

        return cleaned_data


# Optional: Form for quantity update (if using dedicated form submission instead of simple links/buttons)
class UpdateQuantityForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1, widget=forms.NumberInput(attrs={"class": "form-input w-16", "min": "1"})
    )


# DASHBOARD
class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ["first_name", "last_name", "phone_number", "address", "employment_date"]


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["first_name", "last_name", "phone_number", "address"]


class RentalItemTypeForm(forms.ModelForm):
    class Meta:
        model = RentalItemType
        fields = [
            "type_name",
            "description",
            "size",
            "capacity",
            "rental_price_per_day",
            "replacement_cost",
        ]


class RentalItemForm(forms.ModelForm):
    class Meta:
        model = RentalItem
        fields = [
            "item_type",
            "image",
            "status",
            "purchase_date",
            "last_inspection_date",
            "condition_notes",
        ]


class AccessoryForm(forms.ModelForm):
    class Meta:
        model = Accessory
        fields = ["item_type", "accessory_name", "standard_quantity", "replacement_cost"]


class ItemSetForm(forms.ModelForm):
    class Meta:
        model = ItemSet
        fields = ["image", "name", "description", "base_price", "replacement_deposit"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "base_price": forms.NumberInput(attrs={"step": "0.01"}),
            "replacement_deposit": forms.NumberInput(attrs={"step": "0.01"}),
        }


class ItemSetComponentForm(forms.ModelForm):
    class Meta:
        model = ItemSetComponent
        fields = ["item_type", "quantity"]
        widgets = {
            "quantity": forms.NumberInput(attrs={"min": 1}),
        }

    # Add validation to ensure item_type is selected
    def clean_item_type(self):
        item_type = self.cleaned_data.get("item_type")
        if not item_type:
            raise forms.ValidationError("This field is required.")
        return item_type


class ReturnSettlementForm(forms.Form):
    additional_fine_amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        initial=0.00,
        label="ຄ່າປັບໃໝເພີ່ມເຕີມສໍາລັບຄວາມເສຍຫາຍ (ຖ້າມີ)",
        widget=forms.NumberInput(
            attrs={
                "class": "form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 dark:bg-gray-700 dark:border-gray-600 dark:text-white",
                "step": "0.01",
            }
        ),
    )
    fine_description = forms.CharField(
        required=False,
        label="ເຫດຜົນສຳຫຼັບການປັບໃໝ",
        widget=forms.Textarea(
            attrs={
                "class": "form-textarea mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 dark:bg-gray-700 dark:border-gray-600 dark:text-white",
                "rows": 2,
            }
        ),
    )
    final_payment_method = forms.ChoiceField(
        choices=PaymentMethod.choices,
        label="ວິທີການຊຳລະ",
        widget=forms.Select(
            attrs={
                "class": "form-select mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            }
        ),
    )
    final_payment_slip = forms.ImageField(
        required=False,
        label="ສະລິບການໂອນ",
        widget=forms.ClearableFileInput(
            attrs={
                "class": "form-input mt-1 block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400",
                "accept": "image/*",
            }
        ),
    )
    notes_on_return = forms.CharField(
        required=False,
        label="ໝາຍເຫດ",
        widget=forms.Textarea(
            attrs={
                "class": "form-textarea mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 dark:bg-gray-700 dark:border-gray-600 dark:text-white",
                "rows": 3,
            }
        ),
    )

    def clean(self):
        cleaned_data = super().clean()
        additional_fine = cleaned_data.get("additional_fine_amount")
        fine_description = cleaned_data.get("fine_description")
        payment_method = cleaned_data.get("final_payment_method")
        payment_slip = cleaned_data.get("final_payment_slip")

        if additional_fine and additional_fine > 0 and not fine_description:
            self.add_error("fine_description", "Please provide a reason for the additional fine.")

        if (
            payment_method == PaymentMethod.BANK_TRANSFER and not payment_slip
        ):  # Assuming BANK_TRANSFER is a value in PaymentMethod.choices
            self.add_error(
                "final_payment_slip", "Payment slip is required for Bank Transfer settlement."
            )
        return cleaned_data
