from django import forms
from django.db import models

class UploadExperimentParametersForm(forms.Form):

    # following data is kept across 2 diff tables
    user_id = models.IntegerField()
    device = models.CharField(max_length=255)
    grid = models.BooleanField()
    token = models.CharField()

class SendTaskDataForm(forms.Form):
    trial_id = models.IntegerField()
    token = models.CharField()