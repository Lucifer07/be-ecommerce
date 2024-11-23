from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import AnonymousUser
import jwt
from django.conf import settings
from ecommerce.Response.response import Response
class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None 
        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
           raise AuthenticationFailed({'data':"",'message': 'Token expired', 'error': 'TOKEN_EXPIRED'})
        except jwt.InvalidTokenError:
            raise AuthenticationFailed({'data':"",'message': 'Token Invalid', 'error': 'TOKEN_INVALID'})
        return (JWTUser(payload), None)

class JWTUser:
    def __init__(self, payload):
        self.payload = payload

    @property
    def role(self):
        return self.payload.get('role', 'guest')
    def id(self):
        return self.payload.get('id', 0)
    def email(self):
        return self.payload.get('email', "")
    def is_authenticated(self):
        return True
