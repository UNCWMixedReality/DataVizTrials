from django.db import models
#from jsonfield import JSONField

# Create your models here.

class TaskData(models.Model):
    task_id = models.AutoField(primary_key=True)
    category = models.CharField(max_length=255, unique=True)
    num_of_photos = models.IntegerField()

    def __str__(self):
        return self.category

class ImageData(models.Model):

    image_id = models.AutoField(primary_key=True)
    task_id = models.IntegerField()
    image_path = models.TextField()
    texture_path = models.TextField()
    in_category = models.BooleanField()

    def __str__(self):
        return self.first_name

class Environments(models.Model):

    env_id = models.AutoField(primary_key=True)
    device = models.CharField(max_length=255)
    grid = models.BooleanField()
