from django.shortcuts import render
from wand import Image
# Create your views here.
import os

def convertImgToDds(img,path):
    imgName = img[:img.rfind(".")]
    with image.Image(filename=img):
        img.compression = "dxt3"
        img.save(os.path.join(path,imgName+".dds"))
