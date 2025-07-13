from django.shortcuts import render
from rest_framework import generics
from .serializers import UserRegistrationSerializer
from django.contrib.auth.models import User

# Create your views here.

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
