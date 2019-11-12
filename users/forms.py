from django import forms

from .models import UserData

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