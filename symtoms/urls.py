from django.urls import path,include
from symtoms.views import *

urlpatterns = [

#web urls  home
path('dummydata/',dummydata.as_view()),
path('anlaysis_symtoms/',anlaysis_symtoms.as_view()),




]