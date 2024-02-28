from django.contrib import admin
from django.urls import path, include
from symtoms.views import *

urlpatterns = [
    # web urls  home
    path("dummydata/", dummydata.as_view()),
    path("manuplatedata/", manuplatedata.as_view()),
    path("insert_prior_liklyhood/", insert_prior_liklyhood.as_view()),
    path("anlaysis_symtoms/", anlaysis_symtoms.as_view()),
    path("beta/anlaysis_symtoms/", Beta_anlaysis_symtoms.as_view()),
    path("both_symtoms_prediction/", Both_symtoms.as_view()),
    path("anlaysis_prescription/", anlaysis_prescription.as_view()),
    path("updatetier/", updatetier.as_view()),
    path("ekgprediction/", Ekgprediction.as_view()),
    path("recordfeedback/", Recordfeedback.as_view()),
    path("registration/", Registration.as_view()),
    path("login/", Login.as_view()),
]


admin.site.site_header = "Scopium AI"
admin.site.site_title = "Scopium Admin Portal"
admin.site.index_title = "Welcome to Evalutional medical center"