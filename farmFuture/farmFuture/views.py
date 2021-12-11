import pyrebase
from django.shortcuts import render, redirect
from django.contrib import auth
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from farmapp.models import WebUser
from django.contrib.auth import models

config = {
    'apiKey': "AIzaSyCByllLto91nY_iGjo36nFzFzlZ6QFZPBI",
    'authDomain': "farm-a-future.firebaseapp.com",
    'projectId': "farm-a-future",
    'storageBucket': "farm-a-future.appspot.com",
    'messagingSenderId': "20497803793",
    'appId': "1:20497803793:web:745ef4dcf5a0ed24d35fb0",
    "databaseURL": ""
}

firebase = pyrebase.initialize_app(config)
authe = firebase.auth()


def home(request):
    if authe.current_user is not None:
        return render(request, 'welcome.html')
    return render(request, 'login.html')


def handleLogin(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        try:
            user = authe.sign_in_with_email_and_password(email, password)
            if authe.get_account_info(user['idToken'])['users'][0]["emailVerified"] is False:
                try:
                    authe.send_email_verification(user['idToken'])
                    message = "Please verify the email! Link has been sent!"
                except Exception:
                    message = "Please verify the email! Link has been sent!"
                return render(request, 'login.html', {"msg": message})

        except Exception:
            message = "Invalid Credentials"
            return render(request, 'login.html', {"msg": message})

        session_id = user['localId']
        request.session['uid'] = str(session_id)
        return render(request, 'welcome.html')
    return HttpResponseRedirect(reverse("home"))


def handleSignUpUser(request):
    if request.method == "POST":
        email = request.POST.get("email")
        full_name = request.POST.get("fullname")
        password = request.POST.get("password")
        new_user = authe.create_user_with_email_and_password(email, password)
        web_user = WebUser(id=new_user["localId"], full_name=full_name, group=models.Group.objects.filter(name="NormalUser")[0])
        web_user.save()
    return HttpResponseRedirect(reverse("home"))


def handleLogout(request):
    auth.logout(request)
    authe.current_user = None
    return HttpResponseRedirect(reverse("home"))
