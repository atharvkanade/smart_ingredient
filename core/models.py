from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    age = models.PositiveIntegerField(null=True, blank=True)

    health_conditions = models.TextField(
        blank=True,
        help_text="Example: diabetes, BP, thyroid"
    )

    allergies = models.TextField(
        blank=True,
        help_text="Example: peanuts, lactose, gluten"
    )

    dietary_preference = models.CharField(
        max_length=20,
        choices=[
            ('veg', 'Vegetarian'),
            ('non_veg', 'Non-Vegetarian'),
            ('vegan', 'Vegan')
        ],
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} Profile"

class HarmfulIngredient(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class IngredientScan(models.Model):
    INPUT_METHOD_CHOICES = [
        ('scan', 'Scanned'),
        ('manual', 'Manual'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    input_method = models.CharField(
        max_length=10,
        choices=INPUT_METHOD_CHOICES
    )
    ingredients_text = models.TextField()
    warnings = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.input_method} scan by {self.user.username}"
