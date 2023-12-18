import jwt

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, get_object_or_404

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes


from aimproject.settings import SECRET_KEY
from accounts.serializers import UserSerializer
from services.portfolio import PortfolioService


class RegisterAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            PortfolioService.create_account_per_user(user)
            res = Response(
                {
                    "user": serializer.data,
                    "message": "register successs",
                },
                status=status.HTTP_200_OK,
            )
            
            return res
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    
    def post(self, request):
        user = authenticate(
            username=request.data.get("username"),
            password=request.data.get("password"),
        )

        if user is not None:
            serializer = UserSerializer(user)
            login(request, user)
            res = Response(
                {
                    "user": serializer.data,
                    "message": "login success",
                },
                status=status.HTTP_200_OK,
            )
            return res
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    def get(self, request):
        logout(request)
        return Response(status=status.HTTP_202_ACCEPTED)