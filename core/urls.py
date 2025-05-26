from django.conf.urls import handler404
from django.urls import include, path

from . import views as core_views

handler404 = core_views.custom_404_view

urlpatterns = [
    # NOTE: Client Pages
    path("", core_views.home, name="home"),
    path("about/", core_views.about, name="about"),
    path("contact/", core_views.contact, name="contact"),
    path("item/<int:pk>/", core_views.item_detail_view, name="item_detail"),
    # NOTE: Old Single Item Booking (Keep for reference or specific use cases, but primary flow changes)
    path("booking/item/<int:item_pk>/", core_views.create_booking_view, name="create_booking"),
    # NOTE: Booking Selection (Cart) Flow
    path("booking/add/", core_views.add_to_booking_selection, name="add_to_booking_selection"),
    path("booking/selection/", core_views.view_booking_selection, name="view_booking_selection"),
    path(
        "booking/remove/<str:item_type>/<int:pk>/",
        core_views.remove_from_selection,
        name="remove_from_selection",
    ),
    path(
        "booking/update/<str:item_type>/<int:pk>/",
        core_views.update_selection_quantity,
        name="update_selection_quantity",
    ),
    path("booking/finalize/", core_views.finalize_booking, name="finalize_booking"),
    path(
        "booking/success/<int:transaction_pk>/",
        core_views.booking_success_view,
        name="booking_success",
    ),
    # NOTE: Booking History
    path("booking/history/", core_views.booking_history_view, name="booking_history"),
    # --- NOTE: Rental Approval URLs ---
    path(
        "dashboard/rental-approvals/",
        core_views.manage_rental_approvals,
        name="manage_rental_approvals",
    ),
    path(
        "dashboard/rental-approvals/approve/<int:transaction_pk>/",
        core_views.approve_rental,
        name="approve_rental",
    ),
    path(
        "dashboard/rental-approvals/reject/<int:transaction_pk>/",
        core_views.reject_rental,
        name="reject_rental",
    ),
    path(
        "dashboard/rental-transactions/",
        core_views.manage_rental_transactions,
        name="manage_rental_transactions",
    ),
    # NOTE: Dashboard Pages
    path("dashboard/", core_views.dashboard, name="dashboard"),
    # Users
    path("accounts/", include("accounts.urls")),
    path("dashboard/profile", core_views.manage_profile, name="manage-profile"),
    path("dashboard/manage-users/", core_views.manage_users, name="manage-users"),
    path("dashboard/manage-users/delete/<int:pk>/", core_views.delete_user, name="delete-user"),
    # Employees
    path("dashboard/manage-employees/", core_views.manage_employees, name="manage-employees"),
    path(
        "dashboard/manage-employees/edit/<int:pk>/", core_views.edit_employee, name="edit-employee"
    ),
    path(
        "dashboard/manage-employees/delete/<int:pk>/",
        core_views.delete_employee,
        name="delete-employee",
    ),
    # Customers
    path("dashboard/manage-customers/", core_views.manage_customers, name="manage-customers"),
    path(
        "dashboard/manage-customers/edit/<int:pk>/", core_views.edit_customer, name="edit-customer"
    ),
    path(
        "dashboard/manage-customers/delete/<int:pk>/",
        core_views.delete_customer,
        name="delete-customer",
    ),
    # Rental item type
    path(
        "dashboard/manage-rental-item-types/",
        core_views.manage_rental_item_types,
        name="manage-rental-item-types",
    ),
    path(
        "dashboard/manage-rental-item-types/<int:pk>/update/",
        core_views.edit_rental_item_type,
        name="edit-rental-item-type",
    ),
    path(
        "dashboard/manage-rental-item-types/<int:pk>/delete/",
        core_views.delete_rental_item_type,
        name="delete-rental-item-type",
    ),
    # Rental Item
    path(
        "dashboard/manage-rental-items/",
        core_views.manage_rental_items,
        name="manage-rental-items",
    ),
    path(
        "dashboard/manage-rental-items/<int:pk>/update/",
        core_views.edit_rental_item,
        name="edit-rental-item",
    ),
    path(
        "dashboard/manage-rental-items/<int:pk>/delete/",
        core_views.delete_rental_item,
        name="delete-rental-item",
    ),
    # Item Set (NEW)
    path("dashboard/manage-item-sets/", core_views.manage_item_sets, name="manage-item-sets"),
    path(
        "dashboard/manage-item-sets/<int:pk>/update", core_views.edit_item_set, name="edit-item-set"
    ),
    path(
        "dashboard/manage-item-sets/<int:pk>/delete/",
        core_views.delete_item_set,
        name="delete_item_set",
    ),
    path(
        "dashboard/item-set/<int:set_id>/add-components/",
        core_views.add_components,
        name="add_components",
    ),
    path(
        "dashboard/item-set/<int:pk>/delete-components/",
        core_views.delete_item_set_component,
        name="delete-item-set-component",
    ),
    # Accessory
    path(
        "dashboard/manage-accessories/",
        core_views.manage_accessories,
        name="manage-accessories",
    ),
    path(
        "dashboard/manage-accessories/<int:pk>/update/",
        core_views.edit_accessory,
        name="edit-accessory",
    ),
    path(
        "dashboard/manage-accessories/<int:pk>/delete/",
        core_views.delete_accessory,
        name="delete-accessory",
    ),
    # --- NOTE: Return Processing URLs ---
    path("dashboard/returns/", core_views.manage_returns, name="manage_returns"),
    path(
        "dashboard/returns/process/<int:transaction_pk>/",
        core_views.process_return,
        name="process_return",
    ),
    #
    path("dashboard/manage-products/", core_views.manage_products, name="manage-products"),
    # Export Section
    path("dashboard/users/export/", core_views.export_users_excel, name="export_users_excel"),
    path(
        "dashboard/employees/export/",
        core_views.export_employees_excel,
        name="export_employees_excel",
    ),
    path(
        "dashboard/customers/export/",
        core_views.export_customers_excel,
        name="export_customers_excel",
    ),
    path(
        "dashboard/rental-item-types/export/",
        core_views.export_rental_item_types_excel,
        name="export_rental_item_types_excel",
    ),
    path(
        "dashboard/rental-items/export/",
        core_views.export_rental_items_excel,
        name="export_rental_items_excel",
    ),
    path(
        "dashboard/accessories/export/",
        core_views.export_accessories_excel,
        name="export_accessories_excel",
    ),
    path(
        "dashboard/item-sets/export/",
        core_views.export_item_sets_excel,
        name="export_item_sets_excel",
    ),
    path(
        "dashboard/rental-transactions/export/",
        core_views.export_rental_transactions_excel,
        name="export_rental_transactions_excel",
    ),
]
