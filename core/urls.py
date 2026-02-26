from django.urls import path
from .views import register, user_profile
from rest_framework_simplejwt.views import TokenObtainPairView
from .views import analyze_ingredients
from .views import scan_history
from .views import health
from .views import home 


urlpatterns = [
    path('register/', register),
    path('login/', TokenObtainPairView.as_view()),
    path('profile/', user_profile),
    path('analyze/', analyze_ingredients),
    path('history/', scan_history),
    path("health/", health),
    path("", home, name="home"),

]
