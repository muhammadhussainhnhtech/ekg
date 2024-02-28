from rest_framework.permissions import BasePermission
from rest_framework.exceptions import APIException
from rest_framework import status
import jwt




class Authorization(BasePermission):
    def has_permission(self, request, view):
        try:
            jwtkey = "=snzbxs@shak0888"
            tokencatch = request.META['HTTP_AUTHORIZATION'][7:]
            request.GET._mutable = True
            my_token = jwt.decode(tokencatch,jwtkey,algorithms=["HS256"])
            request.GET['token'] = my_token
            return True

        except:
            raise NeedLogin()

class NeedLogin(APIException):
    status_code = 422
    default_detail = {'status': False, 'message': 'Unauthorized'}
    default_code = 'not_authenticated'