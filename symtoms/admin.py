from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Questions)
#admin.site.register(diseases)
#admin.site.register(symtoms)



@admin.register(diseases)
class diseasesAdmin(admin.ModelAdmin):
    list_display = ("name","question")
    search_fields =  ["question__question"]




@admin.register(symtoms)
class symtomsAdmin(admin.ModelAdmin):
    list_display = ("diseasesname","name","probability")
    search_fields =  ["name","diseasesname__question__question"]

