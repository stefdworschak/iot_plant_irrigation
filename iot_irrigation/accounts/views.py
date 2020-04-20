from django.shortcuts import render, redirect, reverse
from accounts.forms import UserLoginForm, UserRegistrationForm


from django.contrib import auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required


# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return redirect(reverse('things_index'))

    if request.method == 'POST':
        login_form = UserLoginForm(request.POST)

        if login_form.is_valid():
            user = auth.authenticate(username=request.POST.get('username'),
                                     password=request.POST.get('password'))
            if user:
                auth.login(user=user, request=request)
                return redirect(reverse('things_index'))
                messages.success(request, "You have successfully logged in!")
            else:
                messages.error(request, 'Username and password combination is wrong.')
    else:
        login_form = UserLoginForm()
    return render(request, 'index.html', {'login_form': login_form})


@login_required
def logout(request):
    """ Log user out """
    auth.logout(request)
    messages.success(request, "You have been logged out!")
    return redirect(reverse('accounts_index'))


def register(request):
    if request.user.is_authenticated:
        return redirect(reverse('things_index'))
    if request.method == 'POST':
        registration_form = UserRegistrationForm(request.POST)
        print(registration_form.is_valid())

        if registration_form.is_valid():
            user = registration_form.save()

            user = auth.authenticate(username=request.POST.get('username'),
                                     password=request.POST.get('password1'))
            if user:
                auth.login(user=user, request=request)
                return redirect(reverse('things_index'))
                messages.success(request, "You have successfully logged in!")
            else:
                messages.error(request, 'Username and password combination is wrong.')
        else:
            for e in registration_form.errors.values():
                messages.error(request, e)
    else:
        registration_form = UserRegistrationForm()

    return render(request, 'registration.html', {'registration_form': registration_form})