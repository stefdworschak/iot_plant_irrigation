from django.db import models

class Record(models.Model):
    thing_name = models.CharField(max_length=255)
    timestamp = models.IntegerField()
    iso_timestamp = models.DateTimeField()
    illuminance = models.FloatField()
    temperature = models.FloatField()
    humidity = models.FloatField()
    soil_probe = models.CharField(max_length=255)

    def __str__(self):
        return "Record " + str(self.id);


