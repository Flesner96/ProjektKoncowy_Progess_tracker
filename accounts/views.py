from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages

class CreateUserView(View):

    def get(self, request):
        return render(request, "accounts/create_user.html")

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        if password != "" and password == password2:
            u = User(username=username)
            u.set_password(password)
            u.save()
            messages.success(request, 'Successfully created user')
            return redirect('base')
        return render(request, "accounts/create_user.html", {"error": "Passwords do not match"})


class LoginView(View):
    def get(self, request):
        return render(request, "accounts/login.html")

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            redirect_url = request.GET.get('next', 'dashboard')
            return redirect(redirect_url)
        else:
            return render(request, "accounts/login.html", {'error': 'Invalid username or password'})

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('base')



