# programs/models.py

from django.db import models

class Program(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    available_spots = models.IntegerField()

    def __str__(self):
        return self.name
