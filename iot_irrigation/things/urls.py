from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='things_index'),
    path('add_thing', views.add_thing, name='add_thing'),
    path('add_credentials', views.add_credentials, name='add_credentials'),
]
