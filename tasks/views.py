from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, JsonResponse

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

# TODO:
# - test bulk add of images n = 5,10,20 :: n=4 done
# - DONE: parameterize "checkVal" functions
# - DONE: parameterize "returnVal" functions
# - DONE: create form w/ file field or image field for imageUpload post req
#   - leaves out files for now... how to do it with multiple?
# - needs better success response
# - deal with csrf exempt

@csrf_exempt
def imageUpload(request):
    if request.method == "POST":
        print(request.FILES)
        data=request.POST
        print(data)
        form = ImageUploadForm(request.POST, {})
        if not form.is_valid():
            print(form.errors.as_json())
            response = json.loads(form.errors.as_json())
            print(response["__all__"][0]["message"])
            return HttpResponse("request isn't valid, "+response["__all__"][0]["message"])
        # if data['token'] not in tokens:
        #     return HttpResponseNotFound("user does not have access privilege")
        if not checkRecordExistence(TaskData, {'category':data['category']}):
            addCategory(data['category'])
        for k,v in request.FILES.items():
            print(v.size)
            print(data['in_category'])
            addImage(data,v)
        return HttpResponse("Got json data")
    else:
        return HttpResponseNotFound()

def addImage(data, photo):
    task = getRecord(TaskData, {"category":data['category']})

    image_object = ImageData()
    image_object.task_id = task.task_id

    folder = ""
    if data['in_category'] == "True":
        image_object.in_category = True
        folder = "positive"
    else:
        image_object.in_category = False
        folder = "negative"
    print("test", image_object.in_category, folder)

    print("adding image to task, n = ", task.num_of_photos)
    task.num_of_photos += 1
    task.save()

    # maybe rename var as original image 
    original_path = os.path.join(dataPath, data['category'], folder, "original", str(task.num_of_photos)+photo.name[photo.name.rfind("."):])
    handle_uploaded_file(original_path, photo)
    image_object.image_path = original_path

    texture_path = os.path.join(dataPath, data['category'], folder, "texture")
    convertImgToDds(original_path, task.num_of_photos, texture_path)
    image_object.texture_path = os.path.join(texture_path, str(task.num_of_photos)+".dds")

    image_object.save()

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