from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import SignUpForm
from django.contrib.auth import logout
from django.contrib.auth.models import User



def signup_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect("signup")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("signup")

        User.objects.create_user(
            username=username,
            password=password1
        )

        messages.success(request, "Account created successfully")

        return redirect("login")

    return render(request, "accounts/signup.html")


# LOGIN

def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect("dashboard")

        else:
            messages.error(
                request,
                "Invalid username or password"
            )

    return render(request, "accounts/login.html")



def logout_view(request):

    logout(request)

    return redirect("login")    