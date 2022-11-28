from django.shortcuts import render, redirect
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate ,logout
from django.contrib import messages
from .forms import NewUserForm
from django.urls import reverse
class Index(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'landing/index.html')

@csrf_exempt
def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("social:post-list")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password")       
    form = AuthenticationForm()
    return render(request=request, template_name="landing/login.html", context={"login_form":form}) 

@csrf_exempt
def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("social:post-list")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    return render(request, "landing/register.html", {"register_form": form})
        
def logout_request(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("landing:index")

