from django.urls import path

from things import views

urlpatterns = [
    path('', views.things, name='things_index'),
    path('add_thing', views.add_thing, name='add_thing'),
    path('delete_thing', views.delete_thing, name='delete_thing'),
    path('add_topic_rule', views.add_topic_rule, name='add_topic_rule'),
]
