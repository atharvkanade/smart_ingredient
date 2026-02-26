from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import UserProfile
from .ai_service import generate_ai_explanation


# -------------------------
# REGISTER API
# -------------------------
@api_view(['POST'])
def register(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {"error": "Username and password are required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {"error": "Username already exists"},
            status=status.HTTP_400_BAD_REQUEST
        )

    User.objects.create_user(
        username=username,
        email=email,
        password=password
    )

    return Response(
        {"message": "User registered successfully"},
        status=status.HTTP_201_CREATED
    )

# -------------------------
# USER PROFILE API (JWT PROTECTED)
# -------------------------
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    user = request.user

    profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == 'GET':
        return Response({
            "username": user.username,
            "age": profile.age,
            "health_conditions": profile.health_conditions,
            "allergies": profile.allergies,
            "dietary_preference": profile.dietary_preference
        })

    if request.method == 'POST':
        profile.age = request.data.get('age')
        profile.health_conditions = request.data.get('health_conditions', '')
        profile.allergies = request.data.get('allergies', '')
        profile.dietary_preference = request.data.get('dietary_preference', '')
        profile.save()

        return Response(
            {"message": "Profile updated successfully"},
            status=status.HTTP_200_OK
        )

from .models import IngredientScan, HarmfulIngredient

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_ingredients(request):
    user = request.user
    input_method = request.data.get('input_method')
    ingredients_text = request.data.get('ingredients_text')

    if not input_method or not ingredients_text:
        return Response(
            {"error": "input_method and ingredients_text are required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    ingredients = [
        i.strip().lower()
        for i in ingredients_text.split(',')
        if i.strip()
    ]

    warnings = []

    # 1️⃣ Check against user allergies
    profile = getattr(user, 'userprofile', None)
    if profile and profile.allergies:
        user_allergies = [
            a.strip().lower()
            for a in profile.allergies.split(',')
        ]
        for ing in ingredients:
            if ing in user_allergies:
                warnings.append(
                    f"⚠️ Contains your allergen: {ing}"
                )

    # 2️⃣ Check harmful ingredients database
    harmful_db = HarmfulIngredient.objects.all()
    harmful_names = [h.name.lower() for h in harmful_db]

    for ing in ingredients:
        if ing in harmful_names:
            warnings.append(
                f"❌ Harmful ingredient detected: {ing}"
            )

    # Save scan
    IngredientScan.objects.create(
        user=user,
        input_method=input_method,
        ingredients_text=ingredients_text,
        warnings=warnings
    )

    user_profile_data = {
    "age": profile.age if profile else None,
    "health_conditions": profile.health_conditions if profile else "",
    "allergies": profile.allergies if profile else "",
    "dietary_preference": profile.dietary_preference if profile else ""
   }

    ai_explanation = generate_ai_explanation(
    user_profile=user_profile_data,
    ingredients=ingredients,
    warnings=warnings
    )


    return Response({
        "input_method": input_method,
        "ingredients": ingredients,
        "warnings": warnings if warnings else ["✅ No known issues detected"],
         "ai_explanation": ai_explanation
    })

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import IngredientScan

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def scan_history(request):
    scans = IngredientScan.objects.filter(user=request.user).order_by('-id')

    data = []
    for scan in scans:
        data.append({
            "id": scan.id,
            "input_method": scan.input_method,
            "ingredients_text": scan.ingredients_text,
            "warnings": scan.warnings,
            "created_at": scan.created_at,
        })

    return Response(data)
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(["GET"])
def health(request):
    return Response({"status": "ok"})
from django.shortcuts import render
from .ai_service import generate_ai_explanation

def home(request):
    result = None

    if request.method == "POST":
        ingredients = request.POST.get("ingredients")

        # Temporary values (we improve later)
        user_profile = "General user with no specific allergies"
        warnings = ingredients  # simple pass-through for now

        result = generate_ai_explanation(
            user_profile=user_profile,
            ingredients=ingredients,
            warnings=warnings
        )

    return render(request, "core/index.html", {"result": result})