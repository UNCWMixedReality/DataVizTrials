
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