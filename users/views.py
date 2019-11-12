from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

from django.template import loader

from .forms import UserDataForm, RecordConsentForm, RetrieveUserDataForm
from .models import UserData

from random import randint

def index(request):
    #template = loader.get_template('index.html')
    return render(request, "index.html")  # error if "template" var is used ...

def signup(request):
    if request.method == "POST":
        form = UserDataForm(request.POST)
        if form.is_valid(): # what is checked here? follows type information?
            user = form.save(commit=False)
            #user.published_date = timezone.now() ## ---> TODO: should this feature be added?
            user.pin = generateUsablePin()
            request.session['pin'] = user.pin
            user.save()
            template = loader.get_template("consentForm.html")
            return HttpResponseRedirect('/consentForm')
    else:
        form = UserDataForm
        return render(request, 'signup.html', {'form': form})

# TODO: what to do if they log out by accident before responding to consent form?
def recordConsent(request):
    if checkLogin(request) == False:
        return HttpResponseRedirect('/signup')
    
    pin = request.session['pin']
    user = UserData.objects.get(pin=pin)

    if request.method == "POST":
        if request.POST.get("yes") == "Val1":
            # access session; get user; redirect to next page w/ pin
            template = loader.get_template('showUserInfo.html')
            user.waiver = True
            context = {
                'user': user,
            }
            return HttpResponse(template.render(context, request))
        else:
            user.waiver = False
            return HttpResponse("<h2> Thank you for your time. </h2>")
        # log user out
        del request.session['pin'] 
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
                    user = UserData.objects.get(pin=int(form.data['pin']))
                    userFound = True
                except:
                    pass
            elif (nameGiven and not pinGiven) or bothGiven:
                try:
                    user = UserData.objects.filter(first_name=form["first_name"].value(), last_name=form["last_name"].value())[0]
                    userFound = True
                except:
                    pass
            else:
                return HttpResponseRedirect('/validate')
            
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

# eventually wont work with a LOT of participants
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

# TODO: what if there are multiple users with the same full name? 
def checkUser(first_name, last_name):
    try:
        UserData.objects.filter(first_name=first_name, last_name=last_name)
        return True
    except:
        return False

def checkPin(pin):
    try:
        UserData.objects.get(pin=pin)
        return True
    except:
        return False

def generatePin():
    pin = randint(1000, 9999)
    return pin

# not being called right now
def returnUser(pin):
    if checkPin(pin):
        user = UserData.objects.get(pin=pin)
        return [user.first_name, user.last_name]
    else:
        return "Try a different pin"

# not being called right now
def returnPin(first_name, last_name):
    if checkUser(first_name, last_name):
        return UserData.objects.filter(first_name=first_name, last_name=last_name)[0].pin
    else:
        return "This user is not registered"