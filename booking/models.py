from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    contact_number = models.CharField(max_length=10)
    age = models.IntegerField()

    def __str__(self):
        return self.user.username
    


class Appointment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    full_name = models.CharField(max_length=100, default="abc")
    email = models.EmailField()
    contact = models.CharField(max_length=15, default="avd")
    date = models.DateField()
    time = models.TimeField()
    department = models.CharField(max_length=100, default="General")
    symptoms = models.TextField(blank=True,max_length=100)

    def __str__(self):
        return f"{self.full_name} - {self.date} ({self.department})"
