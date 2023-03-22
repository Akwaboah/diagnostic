from datetime import datetime
from django.db.models import F
from django.core.serializers.json import DjangoJSONEncoder
from I_CARE.models import Consulting_Room,Patients, User_Details,\
    Business_Info,Procedures,Referring_Facilities,Insurance,Modalities
from I_CARE.utils import user_levels,med_dent_types,investigations_types,hospital_departments

  
def global_data(request):
    bus_info=Business_Info.objects.first()
    pat_data=Patients.objects.all().order_by('Date_Joined')
    total_pat=pat_data.values('Patient_Id').distinct().count()
    debt_pat=pat_data.filter(Balance__lt=0).values('Patient_Id').distinct().count()
    today_pat=pat_data.filter(Last_Visit__date=datetime.now()).values('Patient_Id').distinct().count()
   
    user_info=None
    if request.user.is_authenticated and request.user.is_anonymous==False:
        user_info=User_Details.objects.get(User=request.user)
    
    
    return {'bus_info':bus_info,'hospital_departments':hospital_departments,
    'ward_rooms':Consulting_Room.objects.all(),'procedures':Procedures.objects.all().order_by('Procedure'),
    'total_pat':total_pat,'pat_data':pat_data,'today_pat':today_pat,'debt_pat':debt_pat,
    'user_info':user_info,'groups_level':dict(user_levels),
    'med_dent_types':dict(med_dent_types),'invest_types':dict(investigations_types),'modalities':Modalities.objects.all(),
    'referring_facilities':Referring_Facilities.objects.all().order_by('id'),'accpet_insurance':Insurance.objects.all().order_by('-id')}