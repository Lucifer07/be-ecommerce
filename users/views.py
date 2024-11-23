from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RegisterSerializer, LoginSerializer, LogoutSerializer
from django.contrib.auth import authenticate
from ecommerce.Response.response import Response
class RegisterView(APIView):
    def post(self, request):
        if request.user.is_authenticated:
            return Response(message="Already authenticated", error="ALREADY_AUTHENTICATED", status=400).Send()
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(message="User created successfully", status=201).Send()
        return Response(data=serializer.errors, error="INVALID_DATA", status=400).Send()


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return Response(message="Already authenticated", error="ALREADY_AUTHENTICATED", status=400).Send()
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            refresh.payload['email'] = user.email
            refresh.payload['role'] = user.role  
            refresh.payload['id'] = user.id
            return Response(data={
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }, message="Login successful", status=200).Send()
        return Response(message="Invalid credentials", error="INVALID_CREDENTIALS", status=400).Send()


class LogoutView(APIView):
    def post(self, request):
        if not request.user.is_authenticated:
            return Response(message="Not authenticated", error="NOT_AUTHENTICATED", status=400).Send()
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(message="Logout successful", status=200).Send()
        return Response(data=serializer.errors, error="INVALID_DATA", status=400).Send()
