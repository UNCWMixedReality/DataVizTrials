import os, json
def checkRecordExistence(model, filter):
    try:
        model.objects.get(**filter)
        return True
    except:
        return False

def getRecord(model, filter):
    return model.objects.get(**filter)

# TD: is this necessary if a dictionary can just be written out?
def formatFilter(filterPairs):
    searchDict = {}
    for pair in filterPairs:
        searchDict[pair[0]] = pair[1]
    
    return searchDict

tokensFile = open(os.path.join(os.path.realpath("."),"tokens.txt"), "r")
tokens = tokensFile.readlines()
tokens = [x.strip('\n') for x in tokens]

def handleJsonError(form):
    message = ""
    try:
        print(form.errors.as_json())
        response = json.loads(form.errors.as_json())
        all_errors = [error["message"] for error in response["__all__"]]
        message = "; ".join(all_errors)
        return message
    except:
        return "input are not in the proper form, or are missing"