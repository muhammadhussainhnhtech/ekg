from django.urls import path,include
from symtoms.views import *

urlpatterns = [

#web urls  home
path('dummydata/',dummydata.as_view()),




]