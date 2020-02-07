from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, JsonResponse

from django.template import loader
from django.utils.dateparse import parse_datetime
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

# TODO:
# - DONE: chooseRandomTask - find way to be pseudo-random / equal distribution
# - DONE: may need to use json.loads instead for requests form unity
# - getTaskData - is the output for data even in the proper form??
# - DONE: tokens file redundant to use

@csrf_exempt
def uploadExperimentParameters(request):
    if request.method == 'POST':
        form = UploadExperimentParametersForm(json.loads(request.body), request.FILES)
        if not form.is_valid():
            print(form.errors.as_json())
            response = json.loads(form.errors.as_json())
            print(response["__all__"][0]["message"])
            return HttpResponse("request isn't valid, "+response["__all__"][0]["message"])
        
        if not checkRecordExistence(UserData, {'pin':form.data['userPin']}):
            return HttpResponse("pin not found")
        
        if not checkRecordExistence(Environments, {'device':form.data['Device'], 'grid':form.data['GridInterface']}):
            return HttpResponse("environment conditions not found")

        response = JsonResponse({'TrialID': addTrialToTable(form)})
        return response
    else:
        return HttpResponseNotFound()

# TODO: properly pull and package, (serialize) data and send out
@csrf_exempt
def sendTaskData(request):
    if request.method == 'POST':
        form = SendTaskDataForm(json.loads(request.body), request.FILES)
        if not form.is_valid():
            print(form.errors.as_json())
            response = json.loads(form.errors.as_json())
            print(response["__all__"][0]["message"])
            return HttpResponse("request isn't valid, "+response["__all__"][0]["message"])
        
        if not checkRecordExistence(TrialData, {'trial_id':form.data['TrialID']}):
            return HttpResponse("trial id not found")

        trial = getRecord(TrialData, {'trial_id':form.data['TrialID']})
        task = getRecord(TaskData, {'task_id':trial.task_id})
        response = JsonResponse({'tag': task.category, 'imageTasks': getTaskData(form.data['TrialID'], trial.env_id)})
        return response
    else:
        return HttpResponseNotFound()


# TODO: properly parse and update DBs with json data. 
# - DONE:   prob use deserializer: can it work on dict of dicts? : YES
# - needs to validate data in request about experiment. what if start time is missing?
@csrf_exempt
def uploadExperimentData(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        form = SendTaskDataForm({"token":data['token'], "TrialID":data["TrialID"]}, request.FILES)
        if not form.is_valid():
            print(form.errors.as_json())
            response = json.loads(form.errors.as_json())
            print(response["__all__"][0]["message"])
            return HttpResponse("request isn't valid, "+response["__all__"][0]["message"])
        
        if not checkRecordExistence(TrialData, {'trial_id':data['TrialID']}):
            return HttpResponse("trial id not found")
        
        addInputData(data)

        response = HttpResponse("successful upload")
        return response
    else:
        return HttpResponseNotFound()

def addTrialToTable(form):
    newTrial = TrialData()
    newTrial.user_id = form.data['userPin']
    env = getRecord(Environments, {'device':form.data['Device'], 'grid':form.data['GridInterface']})
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
    if checkRecordExistence(TrialData, {"user_id":user_id}): 
        chosen_task_objects = TrialData.objects.filter("user_id":user_id)
        chosen_task_ids = [task.task_id for task in chosen_task_objects]
        available_task_ids = list(set(all_task_ids)-set(chosen_task_ids))
        return random.choice(available_task_ids)
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
    in_category_images = getObject(ImageData,{"task_id":task_id,"in_category":True})
    not_in_category_images = getObject(ImageData,{"task_id":task_id,"in_category":False})
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
    trial = getRecord(TrialData, {'trial_id':data['TrialID']})
    trial.trial_start = parse_datetime(data['StartTime']) # convert to datetime?
    env = getRecord(Environments, {'env_id':trial.env_id}) # list or single
    grid = env.grid

    num_correct = 0
    for i in range(1,len(data['imageTasks'])+1):
        input = InputData()
        input.trial_id = data['TrialID']
        input.image_id = data.imageTasks[i].photoID
        if data.imageTasks[i].userCorrect == "true": # what does actual value look like?
            input.correct = True
            num_correct += 1
        else:
            input.correct = False            
        if data.imageTasks[i].userUndo == "true": # what does actual value look like?
            input.undo = True
        else:
            input.undo = False
        input.user_decision_points = json.dumps(data.imageTasks[i].userDecisionPoints)
        input.input_end = parse_datetime(data.imageTasks[i].userDecisionPoints[-1][0])
        if grid or (not grid and i == 1):
            input.input_start = parse_datetime(trial.trial_start)
        else:
            input.input_start = parse_datetime(data.imageTasks[i].userDecisionPoints[i-1][0])
        input.save()
    trial.trial_end = parse_datetime(data.imageTasks[i].userDecisionPoints[-1][0]) # convert to datetime?
    trial.score = num_correct / len(data['imageTasks'])
    trial.save()