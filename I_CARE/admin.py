from django.contrib import admin
# Register your models here.
from I_CARE.models import Exam_Room,User_Details,\
    Business_Info,Procedures,Referring_Facilities,\
    Modalities,Approval_Authority,Vitals

admin.site.register(Exam_Room)
admin.site.register(User_Details)
admin.site.register(Business_Info)
admin.site.register(Procedures)
admin.site.register(Referring_Facilities)
admin.site.register(Modalities)
admin.site.register(Approval_Authority)
admin.site.register(Vitals)



