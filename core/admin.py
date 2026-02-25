from django.contrib import admin
from .models import UserProfile
from .models import HarmfulIngredient, IngredientScan

admin.site.register(HarmfulIngredient)
admin.site.register(IngredientScan)
admin.site.register(UserProfile)
