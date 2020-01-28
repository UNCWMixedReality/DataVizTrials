from django.db import models
from jsonfield import JSONField

# Create your models here.

class TrialData(models.Model):

    trial_id = models.AutoField(primary_key=True)
    # ForeignKey.to_field usage?
    user_id = models.IntegerField()
    task_id = models.IntegerField()
    env_id = models.IntegerField()

    trial_start = models.DateTimeField(null=True)
    trial_end = models.DateTimeField(null=True)

    score = models.FloatField(null=True)

    def __str__(self):
        return str(self.trial_id)

class InputData(models.Model):

    image_id = models.IntegerField()
    trial_id = models.IntegerField()
    correct = models.BooleanField()
    input_start = models.DateTimeField()
    input_end = models.DateTimeField()
    undo = models.BooleanField(null=True) # remove null when db reset
    user_decision_points = JSONField(null=True) # remove null when db reset

    def __str__(self):
        return str([self.trial_id, self.image_id])