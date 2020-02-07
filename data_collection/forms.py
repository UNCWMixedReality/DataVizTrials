from django import forms
from django.db import models

from django.forms import ValidationError
from DataVizTrials.general import tokens

class UploadExperimentParametersForm(forms.Form):

    # following data is kept across 2 diff tables
    userPin = models.IntegerField()
    Device = models.CharField(max_length=255)
    GridInterface = models.BooleanField()
    token = models.CharField()

    def clean(self):
        cd = self.cleaned_data

        token = cd.get("token")
        if token not in tokens:
            raise ValidationError(("user does not have access privilege"),code="invalid")
        return cd

class SendTaskDataForm(forms.Form):
    TrialID = models.IntegerField()
    token = models.CharField()

    def clean(self):
        cd = self.cleaned_data

        token = cd.get("token")
        if token not in tokens:
            raise ValidationError(("user does not have access privilege"),code="invalid")
        return cd