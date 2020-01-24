from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound

from django.template import loader
from wand import image
import json

from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response

from DataVizTrials.general import *
from .forms import ImageUploadForm
from .models import TaskData, ImageData

# Create your views here.
import os

dataPathFile = open(os.path.join(os.path.realpath("."),"tasks/datapath.txt"), "r")
dataPath = dataPathFile.readline().strip('\n')

tokensFile = open(os.path.join(os.path.realpath("."),"tokens.txt"), "r")
tokens = tokensFile.readlines()
tokens = [x.strip('\n') for x in tokens]

# TODO:
# - deal with csrf exempt
# - test bulk add of images: 5,10,20 :: 4 done
# - DONE: parameterize "checkVal" functions
# - DONE: parameterize "returnVal" functions
# - DONE: create form w/ file field or image field for imageUpload post req
#   - leaves out files for now... how to do it with multiple?

# needs better success response
# maybe form should have ImageField, handle multiple
@csrf_exempt
def imageUpload(request):
    if request.method == "POST":
        print(request.FILES)
        data=request.POST
        form = ImageUploadForm(request.POST, {})
        if not form.is_valid():
            return HttpResponseNotFound("request isn't valid")
        if data['token'] not in tokens:
            return HttpResponseNotFound("user does not have access privilege")
        if not checkRecordExistence(TaskData, formatFilter([('category',data['category'])])):
            addCategory(data['category'])
        for k,v in request.FILES.items():
            print(v.size)
            addImage(data,v)
        return HttpResponse("Got json data")
    else:
        return HttpResponseNotFound()

def addImage(data, photo):
    task = getRecord(TaskData, formatFilter([("category",data['category'])]))

    image_object = ImageData()
    image_object.task_id = task.task_id

    folder = ""
    if data['in_category']:
        image_object.in_category = True
        folder = "positive"
    else:
        image_object.in_category = False
        folder = "negative"
    image_object.save()

    print("adding image to task", task.num_of_photos)
    task.num_of_photos += 1
    task.save()

    # maybe rename var as original image 
    original_path = os.path.join(dataPath, data['category'], folder, "original", str(task.num_of_photos)+photo.name[photo.name.rfind("."):])
    handle_uploaded_file(original_path, photo)
    image_object.image_path = original_path

    texture_path = os.path.join(dataPath, data['category'], folder, "texture")
    convertImgToDds(original_path, task.num_of_photos, texture_path)
    image_object.texture_path = os.path.join(texture_path, str(task.num_of_photos)+".dds")

def addCategory(category):
    addCategoryToTable(category)
    addCategoryToFileSystem(category)

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

def writeFolder (path):
    try:
        # Create target Directory
        os.mkdir(path)
        print("Directory " , path ,  " Created ") 
    except FileExistsError:
        print("Directory " , path ,  " already exists")

def handle_uploaded_file(filePath, f):
    destination = open(filePath, 'wb+')
    # if i do it all in one shot, it has TypeError: a bytes-like object is required, not 'InMemoryUploadedFile'
    for chunk in f.chunks(): 
        destination.write(chunk)
    destination.close()

def convertImgToDds(img,id,path):
    with image.Image(filename=img) as im:
        im.compression = "dxt3"
        im.save(filename=os.path.join(path,str(id)+".dds"))

## is there a way to parameterize this?
# def returnRecord(model, filter):
#     filter = formatFilter(filterPairs)

#     return findRecord(model, searchDict)


#### may not need the following functions anymore
def checkTaskId(id):
    try:
        TaskData.objects.get(task_id=id)
        return True
    except:
        return False

# assumes checkTaskId was called before running this function
def returnTaskId(category):
    task = TaskData.objects.get(category=category)
    return task.task_id

def checkCategory(category):
    try:
        TaskData.objects.get(category=category)
        return True
    except:
        return False

# assumes checkCategory was called before running this function
def returnCategory(id):
    task = TaskData.objects.get(task_id=id)
    return task.category

def checkImageId(id):
    try:
        ImageData.objects.get(image_id=id)
        return True
    except:
        return False

def checkEnvCategories(device, grid):
    try:
        Environments.objects.filter(device=device, grid=grid)
        return True
    except:
        return False

# assumes checkEnvCategories was called before running this function
def returnEnvId(device, grid):
    environment = Environments.objects.get(device=device, grid=grid)
    return environment.env_id