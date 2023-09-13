from django.urls import path,include
from symtoms.views import *

urlpatterns = [

#web urls  home
path('dummydata/',dummydata.as_view()),
path('manuplatedata/',manuplatedata.as_view()),
path('insert_prior_liklyhood/',insert_prior_liklyhood.as_view()),
path('anlaysis_symtoms/',anlaysis_symtoms.as_view()),
path('updatetier/',updatetier.as_view()),
path('ekgprediction/',Ekgprediction.as_view()),




]