from django.shortcuts import render
import requests
from django.http import JsonResponse
import json
import mysql.connector
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from .models import stock_info
from .ai import ai_advice
from threading import Thread

def homepage(request):
    return render(request, 'homepage.html', {})

def login(request):
    return render(request, 'login.html')

def signup(request):
    return render(request, 'signup.html')

def recommended(request):
    username = request.session.get("username")
    if not username:
        return render(request, "login.html", {"error": "You need to log in first."})

    # Connect to the database
    conn = get_db_connection()
    if not conn:
        return render(request, "result.html", {"error": "Database connection failed."})

    cursor = conn.cursor(dictionary=True)
    cursor.execute("USE userinfo")

    # Fetch recommended investments & AI advice from the database
    cursor.execute("""
        SELECT recommended_vehicle, second_best, third_best, fourth_best, AI_advice 
        FROM users WHERE username = %s
    """, (username,))
    user_data = cursor.fetchone()

    cursor.close()
    conn.close()

    if not user_data:
        return render(request, "result.html", {"error": "No investment data found. Complete the questionnaire first."})

    # Load investment data from JSON
    with open("backend/vehicles.json", "r") as file:
        investment_data = json.load(file)

    # Filter investment data based on the user’s recommended options
    recommendations = {
        key: next((inv for inv in investment_data if inv["name"] == user_data[key]), None)
        for key in ["recommended_vehicle", "second_best", "third_best", "fourth_best"]
    }

    return render(request, "result.html", {
        "recommendations": recommendations,
        "ai_advice": user_data["AI_advice"]  # Pass AI advice to the template
    })

def questions(request):
    return render(request, 'questions.html')

def signup_auth(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "Username already taken"}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({"error": "Email already in use"}, status=400)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("use userinfo")
        sql = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
        values = (username, email, password)
        cursor.execute(sql, values)
        conn.commit()

        cursor.close()
        conn.close()

        return JsonResponse({"message": "Signup successful"})

    return JsonResponse({"error": "Invalid request"}, status=400)

def login_auth(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email = data.get("email")
        password = data.get("password")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("USE userinfo")
        sql = "SELECT username FROM users WHERE email = %s AND password = %s"
        cursor.execute(sql, (email, password))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            # Store the username in session (for additional security)
            request.session["username"] = user["username"]
            
            return JsonResponse({
                "message": "Login successful",
                "username": user["username"]
            }, status=200)
        else:
            return JsonResponse({"error": "Invalid username or password"}, status=401)

    return JsonResponse({"error": "Invalid request method"}, status=405)

from threading import Thread

def submit_answers(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)
        parameters = data.get("parameters", {})
        maxParameters = data.get("maxParameters", {})

        username = request.session.get("username")
        if not username:
            return JsonResponse({"error": "User not logged in"}, status=401)

        conn = get_db_connection()
        if not conn:
            return JsonResponse({"error": "Database connection failed"}, status=500)

        cursor = conn.cursor(dictionary=True)
        cursor.execute("USE userinfo")  # Ensure correct DB is used

        # Retrieve user's email
        cursor.execute("SELECT email FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        if not user:
            return JsonResponse({"error": "User not found"}, status=404)
        email = user["email"]

        # Process user preferences
        preferences = {
            key: round((parameters[key] / maxParameters[key]) * 100, 2)
            for key in parameters if maxParameters.get(key, 0) != 0
        }

        # Determine investment recommendations
        best_match, potential_matches = chooseVehicle(preferences)

        # ✅ Return response immediately to allow frontend redirection
        response = JsonResponse({
            "message": "Investment recommendation is being processed.",
            "recommended_vehicle": best_match,
            "redirect_url": "/recommended/"
        }, status=200)

        # ✅ Process AI and update DB in a separate thread
        def process_ai():
            try:
                ai_explanation = ai_advice(preferences, best_match)

                # ✅ Open a new database connection for the AI processing
                db_conn = get_db_connection()
                if not db_conn:
                    print("❌ AI Processing Error: Database connection failed")
                    return
                
                db_cursor = db_conn.cursor()

                # ✅ Ensure correct database is selected before queries
                db_cursor.execute("USE userinfo")

                # ✅ Update AI-generated advice
                db_cursor.execute(
                    "UPDATE users SET AI_advice = %s WHERE username = %s",
                    (ai_explanation, username)
                )
                db_conn.commit()

                db_cursor.close()
                db_conn.close()

            except Exception as e:
                print("❌ AI Processing Error:", str(e))

        # ✅ Start AI processing in a new thread
        thread = Thread(target=process_ai)
        thread.start()

        cursor.close()
        conn.close()
        return response

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

def get_user_info(request):
    username = request.session.get("username")  # Get username from Django session
    if username:
        return JsonResponse({"username": username})
    return JsonResponse({"username": None})


def chooseVehicle(preferences):
    best_match = None
    potential_matches = []
    best_score = float("-inf")

    # Load vehicle information from JSON file
    with open('backend/vehicles.json', 'r') as file:
        vehicleInfo = json.load(file)

    for vehicle in vehicleInfo:
        score = sum(
            100 - abs(preferences[param] - vehicle[param])
            for param in preferences
            if param in vehicle
        )
        if score > best_score:
            best_score = round(score)
            best_match = vehicle["name"]
            potential_matches.append((round(score), vehicle["name"]))

    # Sort and return the top 3 matches
    potential_matches = sorted(potential_matches, key=lambda x: x[0], reverse=True)[1:4]
    potential_matches = [match[1] for match in potential_matches]  # Extract names

    return best_match, potential_matches

DB_CONFIG = {
    "host": "investment-db-restaurant-solver.c.aivencloud.com",
    "port": "27218",
    "user": "avnadmin",
    "password": "AVNS_ZYh3FUdlS7eJkbiS9da",
    "database": "defaultdb",
}
def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None