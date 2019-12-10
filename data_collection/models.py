from django.db import models

# Create your models here.

class TrialData(models.Model):

    trial_id = models.IntegerField()
    user_id = models.IntegerField()
    task_id = models.IntegerField()
    env_id = models.IntegerField()

    trial_start = models.DateTimeField() # could add auto_add_now ...
    trial_end = models.DateTimeField()

    score = models.FloatField()

    def __str__(self):
        return self.trial_id

class InputData(models.Model):

    image_id = models.IntegerField()
    trial_id = models.IntegerField()
    correct = models.BooleanField()
    input_start = models.DateTimeField()
    input_end = models.DateTimeField()

    def __str__(self):
        return self.image_id
