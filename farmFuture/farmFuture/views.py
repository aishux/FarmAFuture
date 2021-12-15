import json
import pyrebase
from django.shortcuts import render, redirect
from django.contrib import auth
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from farmapp.models import WebUser, Cart, Orders
from django.contrib.auth import models
from django.core.files.storage import default_storage

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
storage = firebase.storage()


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
        new_cart = Cart(user=web_user, cart="")
        new_cart.save()
    return HttpResponseRedirect(reverse("home"))


def handleSignUpFarmer(request):
    if request.method == "POST":
        email = request.POST.get("email")
        full_name = request.POST.get("fullname")
        password = request.POST.get("password")
        farmer_id = request.POST.get("farmerid")
        aadhaar_card = request.FILES.get("aadhaarcard")
        account_address = request.POST.get("accadd")

        new_user = authe.create_user_with_email_and_password(email, password)

        file_name = new_user["localId"] + "_aadhaar" + ".pdf"

        default_storage.save(file_name, aadhaar_card)
        storage.child("aadhaars/" + file_name).put("media/" + file_name)
        default_storage.delete(file_name)

        web_user = WebUser(
            id=new_user["localId"], 
            full_name=full_name,
            farmer_id=farmer_id,
            aadhaar_link="https://firebasestorage.googleapis.com/v0/b/farm-a-future.appspot.com/o/aadhaars%2F{}_aadhaar.pdf?alt=media".format(new_user["localId"]),
            request_farmer=True,
            account_address=account_address,
            group=models.Group.objects.filter(name="NormalUser")[0])

        web_user.save()

        new_cart = Cart(user=web_user, cart="")
        new_cart.save()
    return HttpResponseRedirect(reverse("home"))


def handleLogout(request):
    auth.logout(request)
    authe.current_user = None
    return HttpResponseRedirect(reverse("home"))


def shop(request):
    user = WebUser.objects.filter(id=request.session['uid'])[0]
    get_cart = Cart.objects.filter(user=user)[0]
    get_cart = "{}".format(get_cart.cart)
    return render(request, "index.html", {'carty': get_cart})


def update_cart(request):
    #dynamically updating the cart using ajax request
    user = WebUser.objects.filter(id=request.session['uid'])[0]
    new_cart = request.GET.get('cart', None)
    get_cart = Cart.objects.filter(user=user)[0]
    get_cart.cart = new_cart
    get_cart.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def display_cart(request):
    return render(request, "cart.html")


def checkout(request):
    if request.method == "POST":
        user = WebUser.objects.filter(id=request.session['uid'])[0]
        seller_address = request.POST.get("seller_address")
        buyer_address = request.POST.get("buyer_address")
        order_id = request.POST.get("order_id")
        items_json = request.POST.get('itemsJson','')
        item_ids = request.POST.get('item_ids','')
        name = request.POST.get('firstName','')+" "+request.POST.get('lastName','')
        amount = request.POST.get('amount','')
        email = request.POST.get('email','')
        address = request.POST.get('address1','')+" "+request.POST.get('address2','')
        city = request.POST.get('city','')
        state = request.POST.get('state','')
        zip_code = request.POST.get('zip_code','')
        phone = request.POST.get('phone','')

        new_order = Orders(
            user=user,
            buyer_address=buyer_address,
            seller_address=seller_address,
            order_id=order_id,
            items_json=items_json,
            item_ids=item_ids,
            amount=float(amount),
            name=name,
            email=email,
            address=address,
            city=city,
            state=state,
            zip_code=zip_code,
            phone=phone
        )

        new_order.save()

        return JsonResponse({"order_id": order_id})

    return render(request, "checkout.html")


def order_summary(request, order_id):
    current_order = Orders.objects.filter(order_id=order_id)[0]
    items_lst = []
    json_items = json.loads(current_order.items_json)
    for item in json_items:
        items_lst.append(json_items[item])
    return render(request, "order_summary.html", {"curr_order": current_order, "all_items": items_lst})


def user_profile(request):
    all_orders = Orders.objects.filter(user=WebUser.objects.filter(id=request.session['uid'])[0])[:5]
    return render(request, "user_profile.html",{"all_orders":all_orders})