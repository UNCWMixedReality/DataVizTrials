from django.db import models

# Create your models here.

class ImageData(models.Model):

    ##### example data types from user models

    # byteImg = models. # can this have byte?
    # first_name = models.CharField(max_length=32) 
    # last_name = models.CharField(max_length=32)

    # pin = models.PositiveIntegerField( unique=True, null=True)
    # #can also use models.AutoField if we just want to increment the pin.

    # waiver = models.BooleanField(null=True)


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

    