from django.urls import path
from landing.views import Index
from . import views

app_name = 'landing'

urlpatterns = [
    path('', Index.as_view(), name='index'),
    path("login/", views.login_request, name="login"),
    path("register/", views.register_request, name="register"),
    path("logout", views.logout_request, name= "logout"),
]
