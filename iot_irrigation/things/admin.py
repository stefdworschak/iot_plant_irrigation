from django.contrib import admin
from .models import Thing, ThingRule

# Register your models here.
admin.site.register(Thing)
admin.site.register(ThingRule)