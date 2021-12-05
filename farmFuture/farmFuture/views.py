from django.shortcuts import render, redirect
import pyrebase
from django.contrib import auth

config = {
  'apiKey': "AIzaSyCVK5vp7sLTw498zq9Q5u8Zrl6GYy0VO-0",
  'authDomain': "farmassistant-73d72.firebaseapp.com",
  'projectId': "farmassistant-73d72",
  'storageBucket': "farmassistant-73d72.appspot.com",
  'messagingSenderId': "259119633325",
  'appId': "1:259119633325:web:57b8e4cdd4c7a324348724",
  "databaseURL": ""
}

firebase = pyrebase.initialize_app(config)
authe = firebase.auth()

def loginpage(request):
  return render(request,'login.html') 

def postsign(request):
  email = request.POST.get("email")
  password = request.POST.get("password")
  try:
      user = authe.sign_in_with_email_and_password(email,password)
  except:
      message = "Invalid Credentials"
      return render(request,'login.html',{"msg":message}) 
  session_id = user['idToken']
  request.session['uid'] = str(session_id)
  return render(request,'welcome.html') 

def logout(request):
  auth.logout(request) 
  return render(request,'login.html')

