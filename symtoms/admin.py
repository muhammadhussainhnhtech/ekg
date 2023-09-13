from django.contrib import admin
from .models import *
# Register your models here.


#admin.site.register(Questions)
#admin.site.register(diseases)
#admin.site.register(symtoms)


@admin.register(Questions)
class QuestionsAdmin(admin.ModelAdmin):
    list_display = ("version_list","question")
    search_fields =  ["version_list","question"]


@admin.register(diseases)
class diseasesAdmin(admin.ModelAdmin):
    list_display = ("name","question","probability")
    search_fields =  ["question__question","name"]




@admin.register(symtoms)
class symtomsAdmin(admin.ModelAdmin):
    list_display = ("diseasesname","name","probability")
    search_fields =  ["name","diseasesname__question__question"]



@admin.register(Diagnosticinfo)
class DiagnosticinfoAdmin(admin.ModelAdmin):
    list_display = ("name","created_at","updated_at")
    search_fields =  ["name"]
