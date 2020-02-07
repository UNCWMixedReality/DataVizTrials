from django import forms
from django.db import models

from django.forms import ValidationError
from DataVizTrials.general import tokens

## not sure how to set this up when image file is attached too
# test if non-image works here
class ImageUploadForm(forms.Form):
    category = forms.CharField(max_length=255)
    #photos = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
    #photo1 = forms.ImageField()
    #photo2 = forms.ImageField()
    token = forms.CharField()
    in_category = forms.BooleanField(required=False)

    def clean(self):
        cd = self.cleaned_data

        token = cd.get("token")
        if token not in tokens:
            raise ValidationError(("user does not have access privilege"),code="invalid")
        return cd