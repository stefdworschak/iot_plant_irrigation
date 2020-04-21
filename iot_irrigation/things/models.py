from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Thing(models.Model):
    display_name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    policy_name = models.CharField(max_length=255)
    certificate_arn = models.CharField(max_length=255)
    thing_name = models.CharField(max_length=255, unique=True)
    credentials_url = models.CharField(max_length=255, null=True, default=None)
    turned_on=models.BooleanField(default=False)
    def __str__(self):
        return self.thing_name;

class ThingRule(models.Model):
    thing = models.ForeignKey(Thing, related_name="rules", on_delete=models.CASCADE)
    rule = models.CharField(max_length=255)
    action = models.CharField(max_length=255, null=True, default='publish_off')
    def __str__(self):
            return self.action + "when: " + self.rule;
