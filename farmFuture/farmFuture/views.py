from django.shortcuts import render, redirect
import pyrebase

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
auth = firebase.auth()

def loginpage(request):
  return render(request,'login.html') 

def postsign(request):
  email = request.POST.get("email")
  password = request.POST.get("password")
  user = auth.sign_in_with_email_and_password(email,password)
  print(user)
  auth.send_email_verification
  return render(request,'welcome.html') 