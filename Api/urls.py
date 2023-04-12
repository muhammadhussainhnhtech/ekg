from django.urls import path,include
from Api.views import *

urlpatterns = [

#web urls  home
path('prediction',prediction.as_view()),
path('getdropdowndata',getdropdowndata.as_view()),



]