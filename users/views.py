from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    return render(request, 'users/login.html', {'form': form})

def register_view(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Compte créé ! Tu peux maintenant te connecter.')
            return redirect('login')
    return render(request, 'users/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')