import jwt
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.hashers import check_password
from .models import User


def is_logged_in(request):
    token = request.headers['Authorization'][7:]
    if token is None:
        token = request.COOKIES.get('jwt')
    print(token)
    if not token:
        return False
    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return False
    return True
