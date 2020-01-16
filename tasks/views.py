from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound

from django.template import loader
from wand import image
import json

from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response

from .models import TaskData, ImageData

# Create your views here.
import os

dataPathFile = open(os.path.join(os.path.realpath("."),"tasks/datapath.txt"), "r")
dataPath = dataPathFile.readline().strip('\n')

tokensFile = open(os.path.join(os.path.realpath("."),"tasks/tokens.txt"), "r")
tokens = tokensFile.readlines()
tokens = [x.strip('\n') for x in tokens]

@csrf_exempt
#@api_view(['POST'])
def practice(request):
    if request.method == "POST":
        print(request.POST)
        data=request.POST
        if data['token'] not in tokens:
            return HttpResponseNotFound("user does not have access privilege")
        addImage(data,request.FILES.getlist('photo')[0])

        #print(len(request.FILES.getlist('photo')))
        try:
            category = data['category']
        except KeyError:
            HttpResponseNotFound("Malformed data!")
    elif request.method == "GET":
        return HttpResponse("connection established!")
    else:
        return HttpResponseNotFound()

    return HttpResponse("Got json data: " + category)
    #print(category)
    #doing something like create and update database
    #Dont know what to return, just returning the name for verification if nothing return I got error 
    #return Response({"category":category})

def addImage(data, photo):
    category_id = checkCategory(data['category'])

    image_object = ImageData()
    image_object.task_id = category_id
    if data['in_category'] == 'positive':
        image_object.in_category = 1
    else:
        image_object.in_category = 0
    image_object.save()

    updateCategory(category_id)

    original_path = os.path.join(dataPath, data['category'], data['in_category'],"original", str(image_object.image_id)+".jpg")
    handle_uploaded_file(original_path, photo)
    image_object.image_path = original_path

    texture_path = os.path.join(dataPath, data['category'], data['in_category'],"texture")
    convertImgToDds(original_path, image_object.image_id, texture_path)
    image_object.texture_path = os.path.join(texture_path, str(image_object.image_id)+".dds")

def checkCategory(category):
    # if in database, increment by 1, return ID
    # if not, add to database, return ID
    
    result = TaskData.objects.filter(
        category__contains=category
    )

    if len(result) == 0:
        addCategoryToFileSystem(category)
        # assumes last save was the most recent addition
        # can do another checkCategory function here
        id = addCategoryToTable(category)
        return id
    elif len(result) == 1:
        return result[0].task_id
    else:
        pass

def updateCategory(category_id):
    category_object = TaskData.objects.get(task_id=category_id)
    currentSize = category_object.num_of_photos
    TaskData.objects.get(task_id=category_id).num_of_photos=currentSize+1

def addCategoryToTable(category):
    newTask = TaskData()
    newTask.category = category
    newTask.num_of_photos = 0
    newTask.save()
    return newTask.task_id

def addCategoryToFileSystem(category):
    writeFolder(os.path.join(dataPath, category))
    writeFolder(os.path.join(dataPath, category, 'positive'))
    writeFolder(os.path.join(dataPath, category, 'negative'))

    writeFolder(os.path.join(dataPath, category, 'positive', 'original'))
    writeFolder(os.path.join(dataPath, category, 'negative', 'original'))
    writeFolder(os.path.join(dataPath, category, 'positive', 'texture'))
    writeFolder(os.path.join(dataPath, category, 'negative', 'texture'))

def handle_uploaded_file(filePath, f):
    destination = open(filePath, 'wb+')
    # if i do it all in one shot, it has TypeError: a bytes-like object is required, not 'InMemoryUploadedFile'
    for chunk in f.chunks(): 
        destination.write(chunk)
    destination.close()

def convertImgToDds(img,id,path):
    #imgName = img[:img.rfind(".")]
    with image.Image(filename=img) as im:
        im.compression = "dxt3"
        im.save(filename=os.path.join(path,str(id)+".dds"))

def writeFolder (path):
    try:
        # Create target Directory
        os.mkdir(path)
        print("Directory " , path ,  " Created ") 
    except FileExistsError:
        print("Directory " , path ,  " already exists")

# https://stackoverflow.com/questions/18266543/how-can-i-get-file-name-from-request-file-in-django
# https://stackoverflow.com/questions/40221329/upload-picture-to-django-from-python-script