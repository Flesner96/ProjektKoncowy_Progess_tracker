from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages

class CreateUserView(View):

    def get(self, request):
        return render(request, "accounts/create_user.html")

    def post(self, request):
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password != "" and password == password2:
            try:
                u = User.objects.create_user(username=username, email=email, password=password)
                messages.success(request, 'Successfully created user')
                return redirect('base')
            except IntegrityError:
                return render(request, "accounts/create_user.html", {"error": "Username or email already taken"})
        else:
            return render(request, "accounts/create_user.html", {"error": "Passwords do not match"})


class LoginView(View):
    def get(self, request):
        form = AuthenticationForm()
        return render(request, "base.html", {'form': form})

    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            redirect_url = request.GET.get('next', 'dashboard')
            return redirect(redirect_url)
        return render(request, "base.html", {'form': form})

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('base')

@login_required
def manage_account(request):
    return render(request, 'accounts/manage_account.html')

@login_required
def change_email(request):
    if request.method == 'POST':
        new_email = request.POST.get('email')
        request.user.email = new_email
        request.user.save()
        messages.success(request, 'Email successfully changed.')
        return redirect('manage_account')
    return redirect('manage_account')

class ChangePasswordView(View):
    def get(self, request):
        form = PasswordChangeForm(user=request.user)
        return render(request, 'accounts/change_password.html', {'form': form})

    def post(self, request):
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important for keeping the user logged in after password change
            messages.success(request, 'Your password was successfully updated!')
            return redirect('manage_account')
        else:
            messages.error(request, 'Please correct the error below.')
        return render(request, 'accounts/change_password.html', {'form': form})

class DeleteAccountView(View):
    def get(self, request):
        return render(request, 'accounts/delete_account.html')

    def post(self, request):
        if "confirm" in request.POST:
            user = request.user
            logout(request)
            user.delete()
            messages.success(request, 'Your account has been deleted.')
            return redirect('home')  # Redirect to home or any other page after deletion
        else:
            return render(request, 'accounts/delete_account.html')
