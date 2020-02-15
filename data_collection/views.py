from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, JsonResponse

from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response

from DataVizTrials.general import*
from DataVizTrials.general import tokens # not needed


from users.models import UserData

from tasks.models import TaskData, ImageData, Environments

from .forms import UploadExperimentParametersForm, SendTaskDataForm
from .models import TrialData, InputData

import os
import base64
import json # for testing
import random
from datetime import datetime

#from django.http.request import QueryDict # was used for testing request inpu

# TODO:
# - DONE: chooseRandomTask - find way to be pseudo-random / equal distribution
# - DONE: may need to use json.loads instead for requests form unity
# - getTaskData - is the output for data even in the proper form??
# - DONE: tokens file redundant to use

@csrf_exempt
def uploadExperimentParameters(request):
    if request.method == 'POST':
        #data =  json.loads(request.body)
        data=request.POST
        print(data)
        form = UploadExperimentParametersForm(data)
        if not form.is_valid():
            text = "request isn't valid: "+ handleJsonError(form)
            return HttpResponse(text)
        if not checkRecordExistence(UserData, {'pin':form.data['user_id']}):
            return HttpResponse("pin not found")
        grid = True
        if form.data['grid'] == "false":
            grid = False
        if not checkRecordExistence(Environments, {'device':form.data['device'], 'grid':grid}):
            return HttpResponse("environment conditions not found")

        response = JsonResponse({'trial_id': addTrialToTable(form)})
        return response
    else:
        return HttpResponseNotFound()

# TODO: properly pull and package, (serialize) data and send out
@csrf_exempt
def sendTaskData(request):
    if request.method == 'POST':
        #data =  json.loads(request.body)
        data=request.POST
        form = SendTaskDataForm(data, request.FILES)
        print(data)
        if not form.is_valid():
            text = "request isn't valid: "+ handleJsonError(form)
            return HttpResponse(text)
        if not checkRecordExistence(TrialData, {'trial_id':form.data['trial_id']}):
            return HttpResponse("trial id not found")

        trial = getRecord(TrialData, {'trial_id':form.data['trial_id']})
        task = getRecord(TaskData, {'task_id':trial.task_id})
        #response = JsonResponse({'category': task.category, 'image_tasks': getTaskData(form.data['trial_id'], trial.env_id)})
        response = JsonResponse({'task_id':trial.task_id})
        return response
    else:
        return HttpResponseNotFound()


# TODO: properly parse and update DBs with json data. 
# - DONE:   prob use deserializer: can it work on dict of dicts? : YES
# - needs to validate data in request about experiment. what if start time is missing?
@csrf_exempt
def uploadExperimentData(request):
    if request.method == 'POST':
        #data = json.loads(request.body)
        data=request.POST
        form = SendTaskDataForm({"token":data['token'], "trial_id":data["trial_id"]}, request.FILES)
        print(data)
        if not form.is_valid():
            text = "request isn't valid: "+ handleJsonError(form)
            return HttpResponse(text)
        if not checkRecordExistence(TrialData, {'trial_id':data['trial_id']}):
            return HttpResponse("trial id not found")
        
        addInputData(data)

        response = HttpResponse("successful upload")
        return response
    else:
        return HttpResponseNotFound()

def addTrialToTable(form):
    newTrial = TrialData()
    newTrial.user_id = form.data['user_id']
    grid = True
    if form.data['grid'] == "false":
        grid = False
    env = getRecord(Environments, {'device':form.data['device'], 'grid':grid})
    newTrial.env_id = env.env_id
    newTrial.task_id = chooseRandomTask(newTrial.user_id) 
    newTrial.save()
    return newTrial.trial_id

# if trial needs to be restarted, there will be an error since an entry exists for it-
# so it won't be chosen again
# should be tested
def chooseRandomTask(user_id):
    all_task_objects = TaskData.objects.all()
    all_task_ids = [task.task_id for task in all_task_objects]
    if checkRecordExistence(TrialData, {user_id:user_id}): 
        chosen_task_objects = TrialData.objects.filter(user_id=user_id)
        chosen_task_ids = [task.task_id for task in chosen_task_objects if task.score==None]
        available_task_ids = list(set(all_task_ids)-set(chosen_task_ids))
        return random.choice(available_task_ids) # assumes there is still a task to return
    else:
        return random.choice(all_task_ids)

def getTaskData(trial_id, env_id):
    env = getRecord(Environments, {"env_id":env_id})
    grid = env.grid
    in_category_num = 24
    not_in_category_num = 6 
    if grid:
        num_of_photos = 40
        not_in_category_num = 10
    trial = getRecord(TrialData, {'trial_id':trial_id})
    task_id = trial.task_id
    in_category_images = list(ImageData.objects.filter(task_id=task_id,in_category=True))
    not_in_category_images = list(ImageData.objects.filter(task_id=task_id,in_category=False))
    image_number = 1
    data = {}
    for images, num_photos in [(in_category_images,in_category_num), (not_in_category_images,not_in_category_num)]:
        random.shuffle(images)
        for image in images[:num_photos]: #assumes num_photos < length of list , ALSO not randomized
            image_dict = {}
            print(image.image_id,image.image_path )
            with open(image.texture_path, mode='rb') as file:
                image_dict["serializedImage"] = base64.b64encode(file.read()).decode('utf-8')
            image_dict["photoId"] = image.image_id
            image_dict["imageCorrect"] = image.in_category
            data[image_number] = image_dict
            image_number = image_number + 1
    return data

def addInputData(data):
    trial = getRecord(TrialData, {'trial_id':data['trial_id']})
    trial.trial_start = datetime.strptime(data['StartTime'], "%Y-%m-%d-%H:%M:%S:%f") # convert to datetime?
    print(trial.trial_start)
    env = getRecord(Environments, {'env_id':trial.env_id}) # list or single
    grid = env.grid

    num_correct = 0
    for i in range(1,len(data['imageTasks'])+1):
        input = InputData()
        input.trial_id = data['trial_id']
        input.image_id = data["imageTasks"][i]["photoID"]
        if data["imageTasks"][i]["userCorrect"] == "true": # what does actual value look like?
            input.correct = True
            num_correct += 1
        else:
            input.correct = False            
        if data["imageTasks"][i]["userUndo"] == "true": # what does actual value look like?
            input.undo = True
        else:
            input.undo = False
        input.user_decision_points = json.dumps(data["imageTasks"][i]["userDecisionPoints"])
        input.input_end = parse_datetime(data["imageTasks"][i]["userDecisionPoints"][-1][0])
        if grid or (not grid and i == 1):
            input.input_start = parse_datetime(trial.trial_start)
        else:
            input.input_start = parse_datetime(data["imageTasks"][i]["userDecisionPoints"][i-1][0])
        input.save()
    trial.trial_end = datetime.strptime(data["imageTasks"][i]["userDecisionPoints"][-1][0], "%Y-%m-%d-%H:%M:%S:%f") # convert to datetime?
    trial.score = num_correct / len(data['imageTasks'])
    trial.save()