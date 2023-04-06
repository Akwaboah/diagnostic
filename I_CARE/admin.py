from django.contrib import admin
# Register your models here.
from I_CARE.models import Exam_Room,User_Details,\
    Business_Info,Procedures,Referring_Facilities,\
    Modalities,Approval_Authority,Vitals,Patients

admin.site.register(Exam_Room)
admin.site.register(User_Details)
admin.site.register(Business_Info)
admin.site.register(Procedures)
admin.site.register(Referring_Facilities)
admin.site.register(Modalities)
admin.site.register(Approval_Authority)

@admin.register(Patients)
class Patients_List(admin.ModelAdmin):
    search_fields=['Patient_Id','Patient_Id__Surname','Patient_Id__First_Name','Date']
    list_filter=['Gender']
    search_help_text='Search by patient name or ID'

@admin.register(Vitals)
class Patients_Procedures_History(admin.ModelAdmin):
    search_fields=['Patient_Id__Surname','Patient_Id__First_Name','Date']
    list_filter=['Procedure']
    search_help_text='Search by patient name or date'



