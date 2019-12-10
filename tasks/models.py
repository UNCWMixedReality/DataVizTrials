from django.db import models
#from jsonfield import JSONField

# Create your models here.

class TaskData(models.Model):
    task_id = models.AutoField(primary_key=True)
    category = models.CharField(max_length=255)
    num_of_photos = models.IntegerField()

    def __str__(self):
        return self.category

class ImageData(models.Model):

    image_id = models.AutoField(primary_key=True)
    task_id = models.IntegerField()
    image_path = models.TextField()
    texture_path = models.TextField()
    in_category = models.BooleanField()

    #serializedPhoto = models.BinaryField()
    #taskCorrect = models.BooleanField()
    #userCorrect = models.BooleanField()
    #userUndo = models.BooleanField()
    #photoID = models.IntegerField(unique=True)
    #taskImage = models.ImageField() # correct field type? need dimension constraints?
    #userDecisionPoints = JSONField()
    #taskDimensions = JSONField() # correct usage?

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

class Environments(models.Model):

    env_id = models.AutoField(primary_key=True)
    device = models.CharField(max_length=255)
    grid = models.BooleanField()
