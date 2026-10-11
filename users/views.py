from django.db import transaction
from django.conf import settings
from django.utils import timezone
from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.sites import requests
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.generics import CreateAPIView
from django.core.cache import cache

from .serializers import (
    RegisterValidateSerializer,
    AuthValidateSerializer,
    ConfirmationSerializer,
    CustomTokenObtainPairSerializer,
)
from .models import ConfirmationCode, CustomUser
import random
import string
from rest_framework_simplejwt.views import TokenObtainPairView


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class AuthorizationAPIView(CreateAPIView):
    serializer_class = AuthValidateSerializer

    def post(self, request):
        serializer = AuthValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(**serializer.validated_data)

        if user:
            if not user.is_active:
                return Response(
                    status=status.HTTP_401_UNAUTHORIZED,
                    data={'error': 'User account is not activated yet!'}
                )

            token, _ = Token.objects.get_or_create(user=user)
            return Response(data={'key': token.key})

        return Response(
            status=status.HTTP_401_UNAUTHORIZED,
            data={'error': 'User credentials are wrong!'}
        )

class RegistrationAPIView(CreateAPIView):
    serializer_class = RegisterValidateSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        # Use transaction to ensure data consistency
        with transaction.atomic():
            user = CustomUser.objects.create_user(
                email=email,
                password=password,
                is_active=False
            )

            code = ''.join(random.choices(string.digits, k=6))

            cache_key = f'confirmation_code_{user.id}'

            if cache.get(cache_key):
                cache.delete(cache_key)

            cache.set(cache_key, code, timeout=300)

        return Response(
            status=status.HTTP_201_CREATED,
            data={
                'user_id': user.id,
                'confirmation_code': code
            }
        )


class ConfirmUserAPIView(CreateAPIView):
    serializer_class = ConfirmationSerializer

    def post(self, request):
        serializer = ConfirmationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data['user_id']
        entered_code = serializer.validated_data.get('code')

        cache_key = f'confirmation_code_{user_id}'
        cached_code = cache.get(cache_key)

        if not cached_code or cached_code != entered_code:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={'error': 'Код подтверждения недействителен или истек'}
            )

        with transaction.atomic():
            user = CustomUser.objects.get(id=user_id)
            user.is_active = True
            user.save()

            token, _ = Token.objects.get_or_create(user=user)

            cache.delete(cache_key)

        return Response(
            status=status.HTTP_200_OK,
            data={
                'message': 'User аккаунт успешно активирован',
                'key': token.key
            }
        )

class GoogleLoginRedirectView(APIView):
    def get(self, request):
        google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "consent",
        }
        query_params = "&".join([f"{k}={v}" for k, v in params.items()])
        full_url = f"{google_auth_url}?{query_params}"
        return redirect(full_url)


class GoogleCallbackView(APIView):
    def get(self, request):
        code = request.GET.get("code")
        if not code:
            return Response({"error": "Код авторизации не предоставлен"}, status=status.HTTP_400_BAD_REQUEST)

        token_url = "https://oauth2.googleapis.com/token"
        payload = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }
        token_response = requests.post(token_url, data=payload)
        token_data = token_response.json()

        access_token = token_data.get("access_token")
        if not access_token:
            return Response({"error": "Не удалось получить токен от Google"}, status=status.HTTP_400_BAD_REQUEST)

        user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        user_info_response = requests.get(user_info_url, headers=headers)
        user_info = user_info_response.json()

        email = user_info.get("email")
        given_name = user_info.get("given_name", "")
        family_name = user_info.get("family_name", "")

        if not email:
            return Response({"error": "Google не предоставил email"}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            user, created = CustomUser.objects.get_or_create(email=email)

            user.first_name = given_name
            user.last_name = family_name

            user.is_active = True

            if created or user.registration_source != 'google':
                user.registration_source = "google"

            user.last_login = timezone.now()
            user.save()

            token, _ = Token.objects.get_or_create(user=user)

        return Response(
            status=status.HTTP_200_OK,
            data={
                "message": "Успешная авторизация через Google",
                "created": created,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "registration_source": user.registration_source,
                "key": token.key,
            }
        )