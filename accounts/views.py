from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import (
    CustomUserCreationForm,
    CustomAuthenticationForm,
    CustomUserChangeForm,
)
from .forms import CustomPasswordResetForm, CustomSetPasswordForm
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.contrib.auth.forms import PasswordResetForm
from django.urls import reverse_lazy
from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from .models import CustomUser
from django.utils.encoding import force_bytes
import random
import string

def page_view(request, page_name):
    titles = {
        "home": "Ivory Hospital - Home",
        "about": "Ivory Hospital - About Us",
        "contact": "Ivory Hospital - Contact Us",
        "services": "Ivory Hospital -  Our Services",
        "register": "Register",
        "login": "Login",
        "profile": "Your Profile",
        "menu": "Menu",
        "booking": "Booking",
    }
    title = titles.get(page_name, "Default Title")
    return render(request, f"{page_name}.html", {"page_title": title})

def generate_username(first_name, last_name):
    base = (first_name + last_name).lower().replace(" ", "")
    suffix = ''.join(random.choices(string.digits, k=5))
    return f"{base}{suffix}"
# Registration View
def register(request):
    message = None
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            username = generate_username(
                form.cleaned_data.get("first_name"),
                form.cleaned_data.get("last_name"),
            )
            form.save()
            message = messages.success(request, f"Registration successful.{username} You can now log in.")
            print("User registration successful with username:", username)
            # Send username to email
            return redirect("accounts:loginAccount")
        else:
            # Log detailed form errors
            print("Form errors:", form.errors.as_json())
            print("Form non-field errors:", form.non_field_errors())
    else:
        form = CustomUserCreationForm()
    return render(
        request, "accounts/register.html", {"form": form, "page_title": "Register", "message":message}
    )

def send_username_to_email(request, user):
    subject = "Your Username for Ivory Hospital"
    email_template_name = "accounts/username_email.html"
    context = {
        "username": user.username,
        "domain": request.META["HTTP_HOST"],
        "site_name": "Ivory Hospital",
        "protocol": "http",
        "user": user,
    }
    email_body = render_to_string(email_template_name, context)
    plain_message = strip_tags(email_body)

    try:
        send_mail(
            subject,
            plain_message,
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )
        messages.success(request, "Username has been sent to your email.")
    except Exception as e:
        messages.error(request, f"Failed to send username: {e}")


def loginUser(request):
    form = CustomAuthenticationForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            try:
                user_obj = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                messages.error(request, "No user found with this email.")
                return render(request, "accounts/login.html", {"form": form, "page_title": "Login"})

            user = authenticate(request, username=user_obj.username, password=password)

            if user is not None:
                if not user.is_active:
                    activation_url = request.build_absolute_uri(
                        reverse("accounts:activate_account", kwargs={
                            "uidb64": urlsafe_base64_encode(force_bytes(user.pk)),
                            "token": default_token_generator.make_token(user),
                        })
                    )
                    activation_message = format_html(
                        "Your account is inactive. Please activate it. <a href='{}'>Activate</a>",
                        activation_url
                    )
                    messages.error(request, activation_message)
                    return redirect("accounts:loginAccount")

                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name}!")
                return redirect("accounts:profile")
            else:
                messages.error(request, "Invalid email or password.")
        else:
            messages.error(request, "Please correct the errors below.")
            print("Form errors:", form.errors)

    return render(request, "accounts/login.html", {
        "form": form,
        "page_title": "Login",
    })

def activate_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Your account has been activated successfully.")
        return redirect("accounts:loginAccount")
    else:
        messages.error(request, "The activation link is invalid or has expired.")
        return redirect("accounts:loginAccount")
# Logout View
def logoutUser(request):
    logout(request)
    return redirect("accounts:loginAccount")


# Profile View
@login_required
def profile(request):
    if request.method == "POST":
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("accounts:profile")
    else:
        form = CustomUserChangeForm(instance=request.user)
    return render(
        request, "accounts/profile.html", {"form": form, "page_title": "Your Profile"}
    )


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save()
            if user.is_doctor:
                if user.role == "doctor":
                    user.doctor_profile.is_active = form.cleaned_data.get(
                        "is_active", user.doctor_profile.is_active
                    )
                    user.doctor_profile.save()
            elif user.is_patients:
                if user.role == "patients":
                    user.patients_profile.is_active = form.cleaned_data.get(
                        "is_active", user.patients_profile.is_active
                    )
                    user.patients_profile.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("accounts:profile")
    else:
        form = CustomUserChangeForm(instance=request.user)

    return render(
        request,
        "accounts/edit_profile.html",
        {"form": form, "page_title": "Edit Profile"},
    )


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save()
            if user.is_doctor:
                if hasattr(user, "doctor_profile"):
                    user.doctor_profile.is_active = form.cleaned_data.get(
                        "is_active", user.doctor_profile.is_active
                    )
                    user.doctor_profile.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("accounts:profile")
    else:
        form = CustomUserChangeForm(instance=request.user)

    return render(
        request,
        "accounts/edit_profile.html",
        {"form": form, "page_title": "Edit Profile"},
    )


def password_reset_request(request):
    # Debugging statement to show the HTTP method used
    print(f"Request method: {request.method}")

    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            user = CustomUser.objects.filter(email=email).first()

            # Debugging statements
            print(f"Received POST request for password reset with email: {email}")
            if user:
                print(f"User found: {user.username}")
            else:
                print("No user found with the provided email.")

            if user:
                subject = "Password Reset Requested"
                email_template_name = "accounts/password_reset_email.html"
                context = {
                    "email": email,
                    "domain": request.META["HTTP_HOST"],
                    "site_name": "Ivory Hospital",
                    "protocol": "http",
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": default_token_generator.make_token(user),
                    "user": user,
                }

                # Debugging statement to check the context being sent in the email
                print("Context for password reset email:", context)

                email_body = render_to_string(email_template_name, context)
                plain_message = strip_tags(email_body)

                # Debugging statement to check the email content
                print("Email body content (HTML):", email_body)
                print("Email body content (Plain text):", plain_message)

                try:
                    send_mail(
                        subject,
                        plain_message,
                        settings.DEFAULT_FROM_EMAIL,
                        [email],
                        fail_silently=False,
                    )
                    print("Password reset email sent successfully.")
                except Exception as e:
                    print(f"Failed to send password reset email: {e}")

                messages.success(request, "Password reset email has been sent.")
                return redirect("accounts:password_reset_done")
            else:
                # You might want to handle the case where no user is found differently
                messages.error(request, "No account found with this email address.")
                return redirect("accounts:password_reset")
        else:
            # Log form errors for debugging
            print("Form errors:", form.errors.as_json())
            # If form is not valid, re-render the form with error messages
            print("Form non-field errors:", form.non_field_errors())
    else:
        form = PasswordResetForm()

    # Debugging statement to show the template rendering
    print("Rendering password_reset_form.html with form:", form)

    return render(
        request,
        "accounts/password_reset_form.html",
        {"form": form, "page_title": "Reset Password"},
    )


def password_reset_done(request):
    return render(
        request,
        "accounts/password_reset_done.html",
        {"page_title": "Password Reset Done"},
    )


def password_reset_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            form = CustomSetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Password has been reset successfully.")
                return redirect("accounts:password_reset_complete")
        else:
            form = CustomSetPasswordForm(user)
        return render(
            request,
            "accounts/password_reset_confirm.html",
            {"form": form, "page_title": "Reset Your Password"},
        )
    else:
        messages.error(request, "The password reset link is invalid or has expired.")
        return redirect("accounts:password_reset")


def password_reset_complete(request):
    return render(
        request,
        "accounts/password_reset_complete.html",
        {"page_title": "Password Reset Complete"},
    )
