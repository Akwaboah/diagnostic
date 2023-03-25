from datetime import datetime,timedelta
import math
from django.db.models import F
from datetime import datetime
from django.db.models import F,Value,ExpressionWrapper,CharField
from django.db.models.functions import Concat
from django.core.serializers.json import DjangoJSONEncoder
from I_CARE.models import Consulting_Room,Patients, User_Details,\
    Business_Info,Procedures,Referring_Facilities,Insurance,Modalities, Vitals
from I_CARE.utils import user_levels,med_dent_types,investigations_types,hospital_departments

# My imports
from django.db.models import Count,Q
from django.db.models.functions import TruncYear
import json
from django.db.models import Sum
  
def global_data(request):
    bus_info=Business_Info.objects.first()
    pat_data=Patients.objects.all().order_by('-Date_Joined')
    total_pat=pat_data.values('Patient_Id').distinct().count()
    debt_pat=pat_data.filter(Balance__lt=0).values('Patient_Id').distinct().count()
    today_pat=pat_data.filter(Last_Visit__date=datetime.now()).values('Patient_Id').distinct().count()
   
    ################ Getting gender ##################
    pat_data = Patients.objects.annotate(year=TruncYear('Date_Joined')).values('year').annotate(
    male_count=Count('id', filter=Q(Gender='Male')),
    female_count=Count('id', filter=Q(Gender='Female')),
    other_count=Count('id', filter=Q(Gender='Other'))
    ).order_by('year')
    chart_data = []
    for data in pat_data:
        chart_data.append({
            'year': data['year'].strftime('%Y'),
            'male_count': data['male_count'],
            'female_count': data['female_count'],
            'other_count': data['other_count']
        })

    # ###############Get Data visitor ##################
    # Generate report from vital model 
    # get today's date
    today = datetime.today()

    # get the date of the most recent Monday
    monday = today - timedelta(days=today.weekday())

    # create a list to store the results
    results = []
    
   # loop through the days of the current week
    for i in range(5):
        # get the date of the current day
        current_date = monday + timedelta(days=i)
        # format the day as a shortened string (e.g. "Mon")
        day = current_date.strftime("%a")
        
        # get the vitals for the current day
        vitals = Vitals.objects.filter(Date=current_date)
        patients = vitals.count()
        
        # loop through the procedures for the current day
        for procedure in Procedures.objects.all():
            # count the number of patients for the current procedure and day
            count = vitals.filter(Procedure=procedure).count()
            # get the total charge for the current procedure and day
            total_charge = vitals.filter(Procedure=procedure).aggregate(Sum('Procedure__Charge'))['Procedure__Charge__sum'] or 0
            
            # create a dictionary to store the results for the current procedure and day
            result = {
                'day': day,
                'procedure': procedure.Procedure,
                'charge': float(round(total_charge,2)),
                'count': count,
                'patients':patients,
            }
            # add the dictionary to the results list
            results.append(result)
    

    return {
    'chart_data': chart_data_json,'visitors':visitors,
    'bus_info':bus_info,'hospital_departments':hospital_departments,

    user_info=None
    if request.user.is_authenticated and request.user.is_anonymous==False:
        user_info=User_Details.objects.get(User=request.user)
    return {'bus_info':bus_info,'hospital_departments':hospital_departments,

    'ward_rooms':Consulting_Room.objects.all(),'procedures':Procedures.objects.all().order_by('Procedure'),
    'total_pat':total_pat,'pat_data':pat_data,'today_pat':today_pat,'debt_pat':debt_pat,
    'user_info':user_info,'groups_level':dict(user_levels),
    'med_dent_types':dict(med_dent_types),'invest_types':dict(investigations_types),'modalities':Modalities.objects.all(),
    'referring_facilities':Referring_Facilities.objects.all().order_by('id'),'accpet_insurance':Insurance.objects.all().order_by('-id')}