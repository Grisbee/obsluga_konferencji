from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, ProfileForm, LoginForm


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Rejestracja zakończona pomyślnie!')
            return redirect('edit_profile')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Witaj, {username}!')
                return redirect('profile')
            else:
                messages.error(request, 'Nieprawidłowa nazwa użytkownika lub hasło.')
        else:
            messages.error(request, 'Nieprawidłowa nazwa użytkownika lub hasło.')
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Wylogowano pomyślnie.')
    return redirect('login')


@login_required
def profile_view(request):
    return render(request, 'users/profile.html')


@login_required
def edit_profile(request):
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Profil zaktualizowany pomyślnie!')
            return redirect('profile')
    else:
        profile_form = ProfileForm(instance=request.user.profile)

    return render(request, 'users/edit_profile.html', {
        'profile_form': profile_form
    })