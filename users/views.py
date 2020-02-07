from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, JsonResponse

from django.template import loader
from django.views.decorators.csrf import csrf_exempt

from DataVizTrials.general import *
from .forms import UserDataForm, RecordConsentForm, RetrieveUserDataForm, GetNameForm
from .models import UserData

from random import randint
import json # for testing

# TODO: 
# - do i need to remove the consent part from the database? prob dont need yes/no anymore
# - DONE: do any functions here need a pin to be used?
# - DONE: parameterize "checkVal" functions
# - DONE: parameterize "returnVal"
# - do request checking in forms?
# - make  render vs httpresponse more consistent... well it has forms
# - making naming consistent
# - should errors be httpresponseerror instead of httpresponse?
# - csrf exempt, way to get around it/ make it safer?
# - use proper form data

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
        return HttpResponse(template.render(context, request))
        return render(request, 'signup.html', {'form': form})

# TODO: what to do if they log out by accident before responding to consent form?
def recordConsent(request):
    if checkLogin(request) == False:
        return HttpResponseRedirect('/users/signup')
    
    pin = request.session['pin']
    user = getRecord(UserData, {"pin": pin})

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
# not being used currently because of security issue: who is allowed to access this?
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
                    user = getRecord(UserData, {"pin":int(form.data['pin'])})
                    userFound = True
                except:
                    pass
            elif (nameGiven and not pinGiven):
                try:
                    user = getRecord(UserData, {"first_name":form["first_name"].value(),"last_name":form["last_name"].value()})                  
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
# TODO:
# -  level 1 else statement needs to be tested
# - should token check happen in forms?
@csrf_exempt
def getName(request):
    if request.method == "POST":
        data=request.POST
        form = GetNameForm(request.POST)
        print(form)
        if not form.is_valid():
            print(form.errors.as_json())
            response = json.loads(form.errors.as_json())
            print(response["__all__"][0]["message"])
            return HttpResponse("request isn't valid, "+response["__all__"][0]["message"])
        #if data['token'] not in tokens:
        #    return HttpResponseNotFound("user does not have access privilege")
        try:    
            if(checkRecordExistence(UserData, {"pin":data["pin"]})):
                print("ok")
                user = getRecord(UserData,{"pin":data["pin"]})
                response = JsonResponse({'name': " ".join([user.first_name, user.last_name])})
                print(json.loads(response.content)['name']) # test
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