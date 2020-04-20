from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='accounts_index'),
    path('login', views.index, name='login'),
    path('logout', views.logout, name='accounts_logout'),
    path('register', views.register, name='register'),
]