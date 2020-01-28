from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, JsonResponse

from django.template import loader

from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response

from DataVizTrials.general import*

from users.models import UserData

from tasks.models import TaskData, ImageData, Environments

from .forms import UploadExperimentParametersForm, SendTaskDataForm
from .models import TrialData, InputData

import os
import base64
import json # for testing
import random

tokensFile = open(os.path.join(os.path.realpath("."),"tokens.txt"), "r")
tokens = tokensFile.readlines()
tokens = [x.strip('\n') for x in tokens]
# Create your views here.

# TODO:
# - chooseRandomTask - find way to be pseudo-random / equal distribution
# - DONE: may need to use json.loads instead for requests form unity
# - getTaskData - is the output for data even in the proper form??

@csrf_exempt
def uploadExperimentParameters(request):
    if request.method == 'POST':
        form = UploadExperimentParametersForm(json.loads(request.body), request.FILES)
        if not form.is_valid():
            return HttpResponse("request isn't valid")
        
        if form.data['token'] not in tokens:
            return HttpResponse("user does not have access privilege")
        
        if not checkRecordExistence(UserData, formatFilter([('pin', form.data['user_id'] )])):
            return HttpResponse("pin not found")
        
        if not checkRecordExistence(Environments, formatFilter([('device', form.data['device']), ('grid', form.data['grid'])])):
            return HttpResponse("environment conditions not found")

        response = JsonResponse({'trial_id': addTrialToTable(form)})
        return response
    else:
        return HttpResponseNotFound()

# TODO: properly pull and package, (serialize) data and send out
@csrf_exempt
def sendTaskData(request):
    if request.method == 'POST':
        form = SendTaskDataForm(json.loads(request.body), request.FILES)
        if not form.is_valid():
            return HttpResponse("request isn't valid")
        
        if form.data['token'] not in tokens:
            return HttpResponse("user does not have access privilege")
        
        if not checkRecordExistence(TrialData, formatFilter([('trial_id', form.data['trial_id'])])):
            return HttpResponse("trial id not found")

        trial = getRecord(TrialData, formatFilter([('trial_id', form.data['trial_id'])]))
        task = getRecord(TaskData, formatFilter([('task_id', trial.task_id)]))
        response = JsonResponse({'tag': task.category, 'image_tasks': getTaskData(form.data['trial_id'])})
        return response
    else:
        return HttpResponseNotFound()


# TODO: properly parse and update DBs with json data. 
# - DONE:   prob use deserializer: can it work on dict of dicts? : YES
@csrf_exempt
def uploadExperimentData(request):
    if request.method == 'POST':
        #form = SendTaskDataForm(request.POST, request.FILES)
        #if not form.is_valid():
        #    return HttpResponseNotFound("request isn't valid")
        
        data = json.loads(request.body)
        if data['token'] not in tokens:
            return HttpResponse("user does not have access privilege")
        
        if not checkRecordExistence(TrialData, formatFilter([('trial_id', data['trial_id'])])):
            return HttpResponse("trial id not found")
        
        addInputData(data)

        response = HttpResponse("successful upload")
        return response
    else:
        return HttpResponseNotFound()

def addTrialToTable(form):
    newTrial = TrialData()
    newTrial.user_id = form.data['user_id']
    env = getRecord(Environments, formatFilter([('device', form.data['device']), ('grid', form.data['grid'])]))
    newTrial.env_id = env.env_id
    newTrial.task_id = chooseRandomTask() 
    newTrial.save()
    return newTrial.trial_id

def chooseRandomTask():
    tasks = TaskData.objects.all()
    random_task = random.choice(tasks)
    return random_task.task_id

def getTaskData(trial_id):
    trial = getRecord(TrialData, formatFilter([('trial_id', trial_id)]))
    task_id = trial.task_id
    images = ImageData.objects.filter(task_id=task_id)
    image_number = 1
    data = {}
    for image in images:
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
    trial = getRecord(TrialData, formatFilter([('trial_id', data['TrialID'])]))
    trial.trial_start = data['StartTime'] # convert to datetime?
    trial.trial_end = data['EndTime'] # convert to datetime?
    env = getRecord(Environments, formatFilter([('env_id', trial.env_id)]))
    grid = env.grid

    num_correct = 0
    for i in range(1,len(data['imageTasks']+1)):
        input = InputData()
        input.trial_id = data['TrialID']
        input.image_id = data.imageTasks[i].photoID
        input.correct = data.imageTasks[i].userCorrect
        if input.correct == True:
            num_correct += 1
        input.undo = data.imageTasks[i].userUndo
        input.user_decision_points = json.dumps(data.imageTasks[i].userDecisionPoints)
        input.input_end = data.imageTasks[i].userDecisionPoints[-1][0]
        if grid or (not grid and i == 0):
            input.input_start = trial.trial_start
        else:
            input.input_start = data.imageTasks[i].userDecisionPoints[i-1][0]
        input.save()
    trial.score = num_correct / len(data['imageTasks'])
    trial.save()