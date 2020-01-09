from django.db import models

# Create your models here.

class TrialData(models.Model):

    trial_id = models.IntegerField()
    user_id = models.IntegerField()
    task_id = models.IntegerField()
    env_id = models.IntegerField()

    trial_start = models.DateTimeField() # could add auto_add_now ...
    trial_end = models.DateTimeField()

    score = models.FloatField()

    def __str__(self):
        return self.trial_id

class InputData(models.Model):

    image_id = models.IntegerField()
    trial_id = models.IntegerField()
    correct = models.BooleanField()
    input_start = models.DateTimeField()
    input_end = models.DateTimeField()

    def __str__(self):
        return self.image_id

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
