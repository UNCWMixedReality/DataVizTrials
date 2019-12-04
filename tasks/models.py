from django.db import models
from jsonfield import JSONField

# Create your models here.

class ImageData(models.Model):

    serializedPhoto = models.BinaryField()
    taskCorrect = models.BooleanField()
    userCorrect = models.BooleanField()
    userUndo = models.BooleanField()
    photoID = models.IntegerField(unique=True)
    taskImage = models.ImageField() # correct field type? need dimension constraints?
    userDecisionPoints = JSONField()
    taskDimensions = JSONField() # correct usage?

    ##### data we're collecting for images

    #     public int photoID
    #     public Texture2D taskImage
    #     public Vector2 taskDimensions
    #     public byte[] serializedPhoto
    #     public bool taskCorrect
    #     public bool userCorrect
    #     public bool userUndo = false
    #     public Dictionary<String, DateTime> userDecisionPoints

    def __str__(self):
        return self.first_name

    