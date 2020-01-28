from django import forms
from django.db import models

## not sure how to set this up when image file is attached too
# test if non-image works here
class ImageUploadForm(forms.Form):
    category = forms.CharField(max_length=255)
    #photos = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
    #photo1 = forms.ImageField()
    #photo2 = forms.ImageField()
    token = forms.CharField()
    in_category = forms.BooleanField(required=False)
    # following data is kept across 2 diff tables