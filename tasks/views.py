from django.shortcuts import render
from wand import Image
# Create your views here.

def convertImgToDds(img):
    imgName = img[:img.rfind(".")]
    with image.Image(filename=img):
        img.compression = "dxt3"
        img.save(filename=imgName+".dds")