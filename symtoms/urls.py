from django.urls import path,include
from symtoms.views import *

urlpatterns = [

#web urls  home
path('anlaysis_symtoms/',anlaysis_symtoms.as_view()),




]