from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound

from django.template import loader
from django.views.decorators.csrf import csrf_exempt

from DataVizTrials.general import *
from .forms import UserDataForm, RecordConsentForm, RetrieveUserDataForm, GetNameForm
from .models import UserData

from random import randint

import psycopg2


# TODO: 
# - getName function level 1 else statement needs to be tested
# - make  render vs httpresponse more consistent
# - csrf exempt, way to get around it/ make it safer?
# - do any functions here need a pin to be used?
# - do i need to remove the consent part from the database? prob dont need yes/no anymore
# - DONE: parameterize "checkVal" functions
# - DONE: parameterize "returnVal"
# - making naming consistent

def index(request):
    #template = loader.get_template('index.html')
    return render(request, "index.html")  # error if "template" var is used ...

def signup(request):
    if request.method == "POST":
        form = UserDataForm(request.POST)
        if not form.is_valid():
            return HttpResponse("request isn't valid")            
        user = form.save(commit=False)
        #user.published_date = timezone.now() ## ---> TODO: should this feature be added?
        user.pin = generateUsablePin()
        request.session['pin'] = user.pin
        user.save()
        #template = loader.get_template("consentForm.html")
        return HttpResponseRedirect('/users/consentForm')
    else:
        form = UserDataForm
        return render(request, 'signup.html', {'form': form})

# TODO: what to do if they log out by accident before responding to consent form?
def recordConsent(request):
    if checkLogin(request) == False:
        return HttpResponseRedirect('/users/signup')
    
    pin = request.session['pin']
    user = getRecord(UserData, formatFilter([("pin", pin)]))

    if request.method == "POST":
        del request.session['pin']
        if request.POST.get("yes"):
            # access session; get user; redirect to next page w/ pin
            template = loader.get_template('showUserInfo.html')
            user.waiver = True
            context = {
                'user': user,
            }
            return HttpResponse(template.render(context, request))
        elif request.POST.get("no"):
            user.waiver = False
            return HttpResponse("<h2> Thank you for your time. </h2>")
    else:
        form = RecordConsentForm
        return render(request, "consentForm.html", {'form': form})

# TODO: what if user types both their name and their pin? go through or just look up the first?
def retrieveUserInfo(request):
    
    if request.method == "POST":
        form = RetrieveUserDataForm(request.POST)

        if form.is_valid():
            nameGiven = form.data['first_name'] and form.data['last_name']
            pinGiven = form.data['pin']
            bothGiven = nameGiven and pinGiven
            
            userFound = False
            if (not nameGiven and pinGiven) or bothGiven :
                try:
                    user = getRecord(UserData, formatFilter([("pin", int(form.data['pin']))]))
                    userFound = True
                except:
                    pass
            elif (nameGiven and not pinGiven):
                try:
                    user = getRecord(UserData, formatFilter([("first_name", form["first_name"].value()),("last_name",form["last_name"].value())]))                    
                    userFound = True
                except:
                    pass
            else:
                return HttpResponseRedirect('/users/validate')
            
            if userFound:
                template = loader.get_template("showUserInfo.html")
                context = {
                    'user': user,
                }
                request.session['pin'] = user.pin
                return HttpResponse(template.render(context, request))
            elif nameGiven:
                return HttpResponse("<p> pin not found for user </p>")
            elif pinGiven:
                return HttpResponse("<p> user not found for pin </p>")
        else:
            return HttpResponse('<h2> Invalid form </h3>')
    
    else:
        form = RetrieveUserDataForm()
        return render(request, 'validate.html', {'form': form})

def checkLogin(request):
    try:
        request.session['pin']
        return True
    except KeyError:
        return False

@csrf_exempt
def getName(request):
    if request.method == "POST":
        form = GetNameForm(request.POST)
        if not form.is_valid():
            return HttpResponse("request isn't valid")
        data=request.POST
        try:    
            if(checkRecordExistence(UserData, formatFilter([("pin",data["pin"])]))):
                user = getRecord(UserData,formatFilter([("pin", data["pin"])]))
                response = HttpResponse()
                response['name'] = " ".join([user.first_name, user.last_name])
                print(response['name'])
                return response
            else:
                return HttpResponse("pin doesn't exist")
        except:
            return HttpResponse("tag not properly provided")
    # this else has not been tested.
    else:
        return HttpResponseNotFound()  

# ultimately wont work with a LOT of participants
def generateUsablePin():
    foundPin = False
    pin = 0
    while foundPin == False:
        pin = randint(1000, 9999)
        try:
            UserData.objects.get(pin=pin)
        except:
            foundPin = True

    return pin

def generatePin():
    pin = randint(1000, 9999)
    return pin

#### may not need the following functions anymore

# TODO: what if there are multiple users with the same full name? 
def checkUser(first_name, last_name):
    try:
        UserData.objects.filter(first_name=first_name, last_name=last_name)
        return True
    except:
        return False

# assumes checkUser was called before running this function
def returnUser(pin):
    user = UserData.objects.get(pin=pin)
    return [user.first_name, user.last_name]

def checkPin(pin):
    try:
        UserData.objects.get(pin=pin)
        return True
    except:
        return False

# assumes checkPin was called before running this function
def returnPin(first_name, last_name):
    #checkUser(first_name, last_name):
    pin = UserData.objects.filter(first_name=first_name, last_name=last_name)[0].pin
    return pin
    #else:
    #    return "This user is not registered"





