from django import forms
from .models import UserData

from django.forms import ValidationError
from DataVizTrials.general import tokens

class UserDataForm(forms.ModelForm):

    class Meta:
        model = UserData
        fields = ('first_name', 'last_name')

class RetrieveUserDataForm(forms.Form):
    first_name=forms.CharField(required=False, initial="")
    last_name=forms.CharField(required=False, initial="")
    pin=forms.IntegerField(required=False, initial="")

# TODO: do we actually need a yes, no answer or just a "btw"
class RecordConsentForm():
    pass

class GetNameForm(forms.Form):
    pin = forms.IntegerField()
    token = forms.CharField()

    def clean(self):
        cd = self.cleaned_data

        token = cd.get("token")
        if token not in tokens:
            raise ValidationError(("user does not have access privilege"),code="invalid")
        return cd