from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import logout, login, authenticate
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .models import CarMake, CarModel
from .populate import initiate
import logging
import json
from .restapis import get_request, analyze_review_sentiments, post_review
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

backend_url = os.getenv('backend_url', default="http://localhost:3030")
sentiment_analyzer_url = os.getenv('sentiment_analyzer_url', default="http://localhost:5000/")

# Get an instance of a logger
logger = logging.getLogger(__name__)

@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data['userName']
        password = data['password']
        user = authenticate(username=username, password=password)
        data = {"userName": username}
        if user is not None:
            login(request, user)
            data = {"userName": username, "status": "Authenticated"}
        else:
            data = {"userName": username, "status": "Invalid credentials"}
        return JsonResponse(data)
    else:
        return JsonResponse({"error": "POST method required"}, status=400)

@csrf_exempt
def logout_request(request):
    logout(request)
    data = {"userName": ""}
    return JsonResponse(data)

@csrf_exempt
def registration(request):
    context = {}
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']
    username_exist = False
    email_exist = False
    try:
        User.objects.get(username=username)
        username_exist = True
    except:
        logger.debug("{} is new user".format(username))
    if not username_exist:
        user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, password=password, email=email)
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
        return JsonResponse(data)
    else:
        data = {"userName": username, "error": "Already Registered"}
        return JsonResponse(data)

def get_cars(request):
    count = CarMake.objects.filter().count()
    print(count)
    if count == 0:
        initiate()
    car_models = CarModel.objects.select_related('car_make')
    cars = []
    for car_model in car_models:
        cars.append({"CarModel": car_model.name, "CarMake": car_model.car_make.name})
    return JsonResponse({"CarModels": cars})

def get_dealerships(request, state="All"):
    if state == "All":
        endpoint = "/fetchDealers"
    else:
        endpoint = "/fetchDealers/" + state
    dealerships = get_request(endpoint)
    if dealerships:
        return JsonResponse({"status": 200, "dealers": dealerships})
    else:
        return JsonResponse({"status": 500, "message": "Error fetching dealers"})




def get_dealer_details(request, dealer_id):
    if dealer_id:
        endpoint = "/fetchDealer/" + str(dealer_id)
        dealership = get_request(endpoint)
        print("Dealership data:", dealership)  # พิมพ์ข้อมูล dealer ออกมาเพื่อตรวจสอบ
        if "error" in dealership:
            return JsonResponse({"status": 500, "message": "Error fetching document"})
        return JsonResponse({"status": 200, "dealer": dealership})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})





def get_dealer_reviews(request, dealer_id):
    if dealer_id:
        endpoint = f"/fetchReviews/dealer/{dealer_id}"
        reviews = get_request(endpoint)
        print("Reviews data:", reviews)  # เพิ่มการพิมพ์ข้อมูล
        if "error" in reviews:
            return JsonResponse({"status": 500, "message": "Error fetching reviews"})
        for review_detail in reviews:
            response = analyze_review_sentiments(review_detail['review'])
            print("Sentiment response:", response)  # เพิ่มการพิมพ์ข้อมูล
            review_detail['sentiment'] = response.get('sentiment', 'neutral')
        return JsonResponse({"status": 200, "reviews": reviews})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})

@csrf_exempt
def add_review(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            data = json.loads(request.body)
            try:
                response = post_review(data)
                return JsonResponse({"status": 200, "message": "Review added successfully"})
            except Exception as e:
                print(f"Exception in posting review: {e}")  # เพิ่มการพิมพ์ข้อมูล
                return JsonResponse({"status": 401, "message": "Error in posting review"})
        else:
            return JsonResponse({"status": 403, "message": "Unauthorized"})
    else:
        return JsonResponse({"status": 400, "message": "Invalid request method"})

def initiate():
    pass
