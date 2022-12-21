from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q # for conditional seraches
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm

# Create your views here.

# rooms = [
#     {"id":1, "name":"Let's Learn Python!"},
#     {"id":2, "name":"Full Stack Development"},
#     {"id":3, "name":"System Design"},
# ]

def loginPage(request):
    page = "login"
    if request.user.is_authenticated:
        return redirect("home")     # prevent authenticated users from accessing login page

    if request.method == "POST":
        email = request.POST.get("email").lower() #username and password from login form
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email)
        except:
             # flash msg, imported after render, redirect
             # messages printed out in main.html template
             # can lookup flash messages in documentation
            messages.error(request, "User does NOT exist") 

        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect("home") 
        else:
            messages.error(request, "Username or Password does NOT exist!!!")

    context = {"page":page}
    return render(request, "base/login_register.html", context)

def logoutUser(request):
    logout(request)
    return redirect("home")

def registerPage(request):
    page = "register"
    form = MyUserCreationForm()
    if request.method=="POST":
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False) # commit=False lets us access user object immediately
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "An error ocured during registration!")
    return render(request, "base\login_register.html", {'form':form})

def home(request):
    # cf {% url 'home' %}?q={{topic.name}} in home.html
    q = request.GET.get("q") if request.GET.get('q') != None else ""
    #__icontains is case insentive... __contains is case sentive
    # Search tutorial:
    # https://learndjango.com/tutorials/django-search-tutorial
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) | # take dunder..topic name from model
        Q(name__icontains=q)        | # Q objects allows OR conditions  
        Q(description__icontains=q)
        ) 
    topics = Topic.objects.all()[0:4]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    context = {"rooms": rooms, "topics":topics, "room_count":room_count, "room_messages":room_messages}
    return render(request, "base/home.html", context)

def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == "POST":
        message = Message.objects.create(
            user=request.user, 
            room = room,
            body = request.POST.get("body")
        )
        room.participants.add(request.user)
        return redirect("room", pk=room.id) # reload page

    context = {"room": room, "room_messages": room_messages, "participants":participants}
    return render(request, "base/room.html", context)

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {"user":user, "rooms":rooms, "topics":topics, "room_messages": room_messages}
    return render(request, "base/profile.html", context)

@login_required(login_url="login") # decorator
def createRoom(request):
        form = RoomForm()
        topics = Topic.objects.all()

        if request.method == "POST":
            topic_name = request.POST.get("topic")
            # use get_or_create() method
            topic, created = Topic.objects.get_or_create(name=topic_name)
            Room.objects.create(
                host = request.user,
                topic = topic,
                name = request.POST.get("name"),
                description = request.POST.get("description"),

            )
            return redirect("home")
        
        context = {"form": form, "topics":topics}
        return render(request, "base/room_form.html", context)

@login_required(login_url="login") # decorator
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance = room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse("You are not allowed here")

    if request.method == "POST":
        topic_name = request.POST.get("topic")
        # use get_or_create() method
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get("name")
        room.topic = topic # from topic, created
        room.description = request.POST.get("description")
        room.save()
        return redirect("home")

    context = {"form":form, "topics":topics, "room":room}
    return render(request, "base/room_form.html", context)

@login_required(login_url="login") # decorator
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse("You are not allowed here")
    
    if request.method == "POST":
        print(request.POST)
        room.delete()
        return redirect("home")

    return render(request, "base/delete.html", {"obj":room})

@login_required(login_url="login") # decorator
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user: #check if message owner
        return HttpResponse("You are not allowed here")
    
    if request.method == "POST":
        print(request.POST)
        message.delete()
        return redirect("home")

    return render(request, "base/delete.html", {"obj":message})

@login_required(login_url="login")
def updateUser(request):
    user=request.user
    form = UserForm(instance = user)
    context = {"form":form}
    if request.method=="POST":
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect("user-profile", pk=user.id)
    return render(request, "base/update-user.html", context)

def topicsPage(request):
    # use q filter
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    context = {'topics': topics}
    return render(request, 'base/topics.html', context)

def activityPage(request):
    room_messages = Message.objects.all()
    context = {"room_messages": room_messages}
    return render(request, "base/activity.html", context)
