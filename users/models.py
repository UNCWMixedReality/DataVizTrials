from django.db import models

# Create your models here.

class UserData(models.Model):
    first_name = models.CharField(max_length=32) 
    last_name = models.CharField(max_length=32)

    pin = models.PositiveIntegerField(primary_key=True)
    #can also use models.AutoField if we just want to increment the pin.

    waiver = models.BooleanField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.first_name
