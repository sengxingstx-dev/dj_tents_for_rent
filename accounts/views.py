from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render

from accounts.forms import RegistrationForm
from accounts.models import Customer


def register_view(request):
    if request.method == "POST":
        try:
            form = RegistrationForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)

                first_name = form.cleaned_data["first_name"]
                last_name = form.cleaned_data["last_name"]
                phone_number = form.cleaned_data["phone_number"]
                address = form.cleaned_data["address"]

                user.save()

                Customer.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    phone_number=phone_number,
                    address=address,
                    user=user,
                )

                # Log the user in after registration
                login(request, user)
                messages.success(request, "Registration successful! You are now logged in.")
                return redirect("home")
        except Exception as e:
            print("ERROR:", str(e))

        # If the form is not valid, display error messages
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{field}: {error}")
    else:
        form = RegistrationForm()

    context = {"form": form}

    return render(request, "accounts/register.html", context)


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)

            if user.is_superuser or user.is_staff:
                return redirect("dashboard")

            # Redirect to the next URL if it exists, otherwise redirect to a default URL
            next_url = request.GET.get("next")

            if next_url:
                return redirect(next_url)

            return redirect("home")
        else:
            messages.error(request, "Invalid email or password.")
    return render(request, "accounts/login.html")


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("home")
