import json
import pyrebase
import os
import pickle
import numpy as np
from django.shortcuts import render, redirect
from django.contrib import auth
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.urls import reverse
from farmapp.models import WebUser, Cart, Orders
from django.contrib.auth import models
from django.core.files.storage import default_storage
from .utils import web, operations_contract, upload_to_ipfs, final_is_delivered, token_address
from . import settings

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
    if request.session.get('uid') is not None:
        user = WebUser.objects.filter(id=request.session['uid'])[0]
        if user.group.name == "Farmer":
            return HttpResponseRedirect(reverse("farmerhome"))
        else:
            return HttpResponseRedirect(reverse("shop"))
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
        request.session['email'] = email
        request.session['usrname'] = email.split("@")[0]
        request.session['uid'] = str(session_id)
    return HttpResponseRedirect(reverse("home"))


def handleSignUpUser(request):
    if request.method == "POST":
        email = request.POST.get("email")
        full_name = request.POST.get("fullname")
        password = request.POST.get("password")
        new_user = authe.create_user_with_email_and_password(email, password)
        web_user = WebUser(id=new_user["localId"], full_name=full_name, group=models.Group.objects.filter(name="NormalUser")[0])
        web_user.save()
        new_cart = Cart(user=web_user, cart="{}")
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

        new_cart = Cart(user=web_user, cart="{}")
        new_cart.save()
    return HttpResponseRedirect(reverse("home"))


def handleLogout(request):
    if request.session.get('uid') is not None:
        auth.logout(request)
        authe.current_user = None
    return HttpResponseRedirect(reverse("home"))


def shop(request):
    if request.session.get('uid') is not None:
        user = WebUser.objects.filter(id=request.session['uid'])[0]
        if user.group.name != "Farmer":
            get_cart = Cart.objects.filter(user=user)[0]
            get_cart = "{}".format(get_cart.cart)
            return render(request, "index.html", {'carty': get_cart})
        else:
            return HttpResponseRedirect(reverse("farmerhome"))
    return HttpResponse('Unauthorized', status=401)


def update_cart(request):
    #dynamically updating the cart using ajax request
    if request.session.get('uid') is not None:
        user = WebUser.objects.filter(id=request.session['uid'])[0]
        new_cart = request.GET.get('cart', None)
        get_cart = Cart.objects.filter(user=user)[0]
        get_cart.cart = new_cart
        get_cart.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def display_cart(request):
    if request.session.get('uid') is not None:
        return render(request, "cart.html")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


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
            phone=phone,
            buyer_delivered=False,
            seller_delivered=False
        )

        new_order.save()

        return JsonResponse({"order_id": order_id})

    return render(request, "checkout.html")


def all_orders(request):
    if request.session.get('uid') is not None:
        user = WebUser.objects.filter(id=request.session['uid'])[0]
        is_farmer = user.group.name == "Farmer"
        if user.group.name == "Farmer":
            all_orders = Orders.objects.filter(seller_address=user.account_address)
        else:
            all_orders = Orders.objects.filter(user=WebUser.objects.filter(id=request.session['uid'])[0])
        return render(request, "all_orders.html",{"all_orders":all_orders, "is_farmer": is_farmer})
    return HttpResponse('Unauthorized', status=401)


def order_summary(request, order_id):
    if request.session.get('uid') is not None:
        user = WebUser.objects.filter(id=request.session['uid'])[0]
        current_order = Orders.objects.filter(order_id=order_id)[0]
        if current_order.user.id == request.session['uid'] or current_order.seller_address == user.account_address:
            items_lst = []
            json_items = json.loads(current_order.items_json)
            for item in json_items:
                items_lst.append(json_items[item])
            return render(request, "order_summary.html", {"curr_order": current_order, "all_items": items_lst})
    return HttpResponse('Unauthorized', status=401)


def user_profile(request):
    if request.session.get('uid') is not None:
        account_address = ""
        farmer_balance = ""
        amount_withdrawable = ""
        user = WebUser.objects.filter(id=request.session['uid'])[0]
        user_email = request.session["email"]
        is_farmer = user.group.name == "Farmer"
        if is_farmer:
            account_address = user.account_address
            farmer_balance = web.eth.getBalance(account_address)
            amount_withdrawable = operations_contract.functions.farmer_to_amount_payable(account_address).call()
            all_orders = Orders.objects.filter(seller_address=user.account_address)[:5]
        else:
            all_orders = Orders.objects.filter(user=user)[:5]
        return render(request, "user_profile.html", {"all_orders": all_orders, "user_name": user.full_name, "user_email": user_email, "is_farmer": is_farmer, "account_address": account_address, "farmer_balance": farmer_balance, "amount_withdrawable":amount_withdrawable})
    return HttpResponse('Unauthorized', status=401)


def add_good(request):
    if request.session.get('uid') is not None:
        user = WebUser.objects.filter(id=request.session['uid'])[0]
        if user.group.name == "Farmer": 
            return render(request, "farmers/addItem.html")
    return HttpResponse('Unauthorized', status=401)


def save_good(request):
    if request.method == "POST":
        user = WebUser.objects.filter(id=request.session['uid'])[0]
        if user.group.name == "Farmer":
            good_name = request.POST.get("good_name")
            token_amount = int((float(request.POST.get("good_price")) / 10)*(10**18))
            image = request.FILES.get("good_image")
            description = request.POST.get("good_desc")

            farmer_address = user.account_address

            image_uri = upload_to_ipfs(image)

            nonce = web.eth.get_transaction_count(web.toChecksumAddress(web.eth.default_account))
            operation_tx = operations_contract.functions.addGoods(farmer_address, good_name, token_amount, image_uri, description).buildTransaction({
                'chainId': 4,
                'gas': 7000000,
                'gasPrice': web.toHex((10**11)),
                'nonce': nonce,
                })
            signed_tx = web.eth.account.sign_transaction(operation_tx, private_key=os.getenv("PRIVATE_KEY"))
            receipt = web.eth.send_raw_transaction(signed_tx.rawTransaction)
            web.eth.wait_for_transaction_receipt(receipt)
            print("Good will be added soon!")

            return HttpResponseRedirect(reverse("addgood"))

    return HttpResponse('Unauthorized', status=401)


def farmer_home(request):
    if request.session.get('uid') is not None:
        user = WebUser.objects.filter(id=request.session['uid'])[0]
        if user.group.name == "Farmer":
            return render(request, "farmers/index.html", {"farmerAddress": user.account_address})
    return HttpResponse('Unauthorized', status=401)


def farmer_withdraw(request, acc_address):
    if request.session.get('uid') is not None:
        user_acc = WebUser.objects.filter(id=request.session['uid'])[0].account_address
        if user_acc == acc_address:
            nonce = web.eth.get_transaction_count(web.toChecksumAddress(web.eth.default_account))
            withdraw_tx = operations_contract.functions.farmerWithdraw(token_address, acc_address).buildTransaction({
                    'chainId': 4,
                    'gas': 700000,
                    'maxFeePerGas': web.toWei('2', 'gwei'),
                    'maxPriorityFeePerGas': web.toWei('1', 'gwei'),
                    'nonce': nonce,
                    })
            signed_tx = web.eth.account.sign_transaction(withdraw_tx, private_key=os.getenv("PRIVATE_KEY"))
            receipt = web.eth.send_raw_transaction(signed_tx.rawTransaction)
            web.eth.wait_for_transaction_receipt(receipt)
            print("Tokens have been withdrawn!")

            return HttpResponseRedirect(reverse("userprofile"))
    else:
        return HttpResponse('Unauthorized', status=401)


def order_delivered(request, order_id):
    if request.session.get('uid') is not None:
        user = WebUser.objects.filter(id=request.session['uid'])[0]
        curr_order = Orders.objects.filter(order_id=order_id)[0]
        if user.group.name == "Farmer" and curr_order.seller_address == user.account_address:
            curr_order.seller_delivered = True
            curr_order.save()
        elif user.group.name != "Farmer" and curr_order.user == user:
            curr_order.buyer_delivered = True
            curr_order.save()
        else:
            return HttpResponse('Unauthorized', status=401)

        if curr_order.seller_delivered and curr_order.buyer_delivered:
            final_is_delivered(int(order_id))

        return HttpResponseRedirect(reverse("allorders"))
    return HttpResponse('Unauthorized', status=401)


def dashboard(request):
    if request.session.get('uid') is not None:
        user = WebUser.objects.filter(id=request.session['uid'])[0]
        if user.group.name == "Farmer":
            return render(request, "farmers/dashboard.html")
    return HttpResponse('Unauthorized', status=401)


def make_prediction(choosen_crops, nitrogen, phosphorous, pottasium, ph, humidity, temperature, rainfall):
    data = np.array([[nitrogen, phosphorous, pottasium, ph, humidity, temperature, rainfall]])
    loaded_model = pickle.load(open(settings.BASE_DIR / "PredictionModel.pkl", "rb"))
    probs = loaded_model.predict_proba(data)
    best_n = np.argsort(probs, axis=1)[0][::-1]
    best_crop = loaded_model.classes_[best_n[0]]
    if choosen_crops != []:
        for i in best_n:
            if loaded_model.classes_[i] in choosen_crops:
                return [loaded_model.classes_[i], best_crop]
    return [None, best_crop]


def predictor(request):
    if request.method == "POST":
        nitrogen = int(request.POST.get("nitrogen"))
        phosphorous = int(request.POST.get("phosphorous"))
        pottasium = int(request.POST.get("pottasium"))
        ph = int(request.POST.get("soilph"))
        humidity = float(request.POST.get("humidity"))
        temperature = float(request.POST.get("temperature"))
        rainfall = float(request.POST.get("rainfall"))
        choosen_crops = request.POST.getlist("choosen_crops")
        prediction = make_prediction(choosen_crops, nitrogen, phosphorous, pottasium, ph, humidity, temperature, rainfall)
        return render(request, "farmers/suggestion.html",{"best_crop": prediction[1], "prediction": prediction[0]})
    return render(request,"farmers/Predictor.html")