from django.db import models
from django.contrib.auth.models import User 

# Create your models here.

class Topic(models.Model):
    name = models.CharField(max_length=200)
    def __str__(self):
        return self.name

class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    # A topic can have ONLY ONE room
    # Keep room if topic (parent) is deleted. 
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True) 
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True) # null for db; blank for form display
    participants = models.ManyToManyField(User, related_name="participants", blank=True)
    updated = models.DateTimeField(auto_now=True) # takes timestamp snapshot everytine 
    created = models.DateTimeField(auto_now_add=True) # only takes timestamp snapshot on creation

    class Meta:
        # show latest updates first
        ordering = ["-updated", "-created"]

    def __str__(self) -> str:
        return self.name #The __str__ method in Python represents the class objects as a string – it can be used for classes. 

class Message(models.Model):
    # One (Room) to many (Messages). If Room (parent) is deleted, messages are also deleted
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE) 
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True) 
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.body[0:50] 

    class Meta:
        # show latest updates first
        ordering = ["-updated", "-created"]


 