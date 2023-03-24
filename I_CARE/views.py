import asyncio
from datetime import datetime,date,time
from django.utils import timezone
from decimal import Decimal
import json
import requests

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render,HttpResponse,redirect
from django.views.generic.base import View
from django.contrib.auth import authenticate,login, logout
from django.contrib.auth.models import Group,User
from django.db import IntegrityError,transaction
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
# Django password hashing and validating imports
from django.contrib.auth.hashers import check_password
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.db.models.functions import Concat,Cast
from django.db.models import F,Value,CharField,Sum,ExpressionWrapper,DecimalField,DateField,Q
from I_CARE.models import Business_Info, Patients, User_Details,Patients_Checker,Vitals,\
    Appoitment,Message,Procedures,Presenting_Complaints,Journal_History,Treatment_Alert,\
    Birthday_Wishes,Stocks_Department,Supplier,Stocks,New_Stocks,Stocks_Checker,Drugs_Prescriptions,\
    Insurance,Referring_Facilities,Requisition,Approval_Authority,Journal_History_Checker,Payment_Journal

from I_CARE.forms import Patients_Form,Staff_Form,Stocks_Form
from I_CARE.decorators import class_allow_users, unauthenticated_staffs
from I_CARE.utils import user_levels

# Manager imports
from collections import defaultdict
from django.apps import apps
# Create your views here.

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        # 👇️ if passed in object is instance of Decimal
        # convert it to a string
        if isinstance(obj, (Decimal,int,date,time)):
            return str(obj)
        # 👇️ otherwise use the default behavior
        return json.JSONEncoder.default(self, obj)

class BulkCreateManager(object):

    def __init__(self,chunk_size=100):
        self._create_queues=defaultdict(list)
        self.chunk_size=chunk_size

    def _commit(self,model_class):
        model_key=model_class._meta.label
        model_class.objects.bulk_create(self._create_queues[model_key])
        self._create_queues[model_key]=[]

    def add(self,obj):
        model_class=type(obj)
        model_key=model_class._meta.label
        self._create_queues[model_key].append(obj)
        if len(self._create_queues[model_key])>=self.chunk_size:
            self._commit(model_class)

    def done(self):
        for model_name, objs in self._create_queues.items():
            if len(objs)>0:
                self._commit(apps.get_model(model_name))

def Loged_User(request)-> str:
    user_data=request.user
    userName='%s %s'%(user_data.first_name,user_data.last_name)
    return userName

def Loged_User_Instance(request):
    user_data=User_Details.objects.get(User=request.user)
    return user_data

def gen_pat_id():
    pat_id=Patients_Checker.objects.all().values('Patient_Id').distinct().count() + 1
    pat_id=str(pat_id).zfill(3)
    return '%s%s'%('OLV',pat_id)
     
def getBusInfo():
    return Business_Info.objects.first()

def saveFacility(referring_facility):
    data=Referring_Facilities.objects.filter(Facility_Name=referring_facility)
    if not data:
        Referring_Facilities.objects.create(Facility_Name=referring_facility)

class SMS:

    def __init__(self,extras=[]):
        self.extras=extras
        self.bus_info=Business_Info.objects.first()

    async def SEND_ALERT(self, receiver:list, msg):
        task_result= await asyncio.create_task(coro=self.CREATE_ALERT(receiver, msg))
        return task_result
             
    async def CREATE_ALERT(self,receiver:list, msg):
        
        try:
            _url = "https://sms.arkesel.com/api/v2/sms/send"
            _payload={
                    "sender": self.bus_info.Bus_Name_Abbr,
                    "message": str(msg),
                    "recipients": receiver
                    }
            _headers = {'api-key':self.bus_info.Sms_Api_Key,
                        'Content-Type': 'application/json'}
            response = requests.request('POST',_url, headers=_headers, data=json.dumps(_payload))
            return json.loads(response.text)
        except requests.exceptions.RequestException as e:
            return ("Poor/Network connection error occured")
    
    # returns the task for the given coroutine or none
    def task_for_coro(self,coro):
        # search for task that is running a given coroutine
        for task in asyncio.all_tasks():
            # check if task is running the coro
            if task.get_coro() is coro:
                return task
        return None

    def SMS_BALANCE(self):
        try:
            url = "https://sms.arkesel.com/sms/api"

            payload = {"action": "check-balance",
                       "api_key": '',
                       "response": "json"}
            response = requests.get(url, params=payload)

            data=json.loads(str(response.text))
            return data
        except requests.exceptions.RequestException as e:
            # raise SystemExit(e)
            pass
 
    def getWLM_MSG(self,first_name):
        # time_sent=str(datetime.now().strftime("%H:%M:%S"))
        # date_sent=str(datetime.now().strftime("%Y-%m-%d"))
        msg="Hi %s, welcome to %s. We are committed in providing our patients the exceptional diagnosis services, a relaxing environment, patient education and expertise they deserve by using the latest diagnosis technology and procedures. Our goal is to partner with our patients to help them achieve and maintain excellent health throughout their lifetime. Discover more on our website at Link:%s, Thank You."%(first_name,self.bus_info.Bus_Name,self.bus_info.Website)
        return msg
    
    def getPAYMENT_MSG(self,first_name,amount):
        msg='Hi %s, your payment of %s has been comfirmed, Thank You.'%(first_name,amount)
        return msg

class CUS_SMS(View):

    def post(self,request, *args,**kwargs):
        if kwargs['page']=='send':
            usr_status='Request delivered successfully'
            sms_init=SMS()
            custom_msg=str(request.POST['custom_msg'])
            forward_to=request.POST['forward_to']
            custom_tel=str(request.POST['custom_tel']).split(',')
            if forward_to == 'Staffs':
                contacts=list(User_Details.objects.all().values_list('Contact',flat=True))
                asyncio.run(sms_init.SEND_ALERT(contacts,custom_msg))
            elif forward_to == 'All Patients':
                contacts=list(Patients.objects.all().values_list('Tel',flat=True))
                asyncio.run(sms_init.SEND_ALERT(contacts,custom_msg))
            elif forward_to == 'Debtor Patient':
                contacts=list(Patients.objects.filter(Balance__lt=0).values_list('Tel',flat=True))
                asyncio.run(sms_init.SEND_ALERT(contacts,custom_msg))
            elif forward_to=='Custom Receiver':
                asyncio.run(sms_init.SEND_ALERT(custom_tel,custom_msg))
            return HttpResponse(json.dumps({'message':usr_status}),content_type='application/json')
        elif kwargs['page']=='tm-msg':
            Treatment_Alert.objects.create(
                Message =request.POST['custom_msg'],
                Treatments = ','.join(request.POST.getlist('tm_type[]')),
                Send_Alert = request.POST['when_to']
            )
            return HttpResponse(json.dumps({'message':'Request completed...'}),content_type='application/json')

class Auth_Staffs(View):
    
    def dispatch(self,  *args, **kwargs):
        return super(Auth_Staffs,self).dispatch(*args, **kwargs)

    def get(self,request,page):
        if page=='profile':
            if request.user.is_authenticated and request.user.is_anonymous==False:
                user_det=User_Details.objects.get(User=request.user)
                user_det=Staff_Form(instance=user_det)
                return render(request,"I_CARE/admin/profile.html",context={'page':'Profile Settings','user_det':user_det})
            else:
                # if not authenticated or is anonymous then redirect to login page
                return redirect('/staff/login')
            
        elif page=='login':
            if request.user.is_authenticated and request.user.is_anonymous==False:
                return redirect("/opd/dashboard")
            else:
                return render(request,"I_CARE/admin/login.html")
        elif page=='logout':
            logout(request)
            return redirect('/staff/login')
        elif page=='forgot-password':
            return render(request,"I_CARE/admin/forgot-password.html") 
             
    @transaction.atomic(using=None, savepoint=True)
    def post(self,request,page):
        if page=='login':
            username = request.POST['username']
            usr_password = str(request.POST['password'])
            try:
                user_data=User.objects.get(username=username)
                test_pass=check_password(usr_password,user_data.password)
                if test_pass:
                    user = authenticate(username=username,password=usr_password)
                    if user:
                        login(request, user)
                        messages.info(request, "Welcome To %s, %s"%(getBusInfo().Bus_Name_Abbr, username))
                        return redirect("/opd/dashboard")
                    else:
                        messages.success(request, "Account disabled, contact support center for more info.")
                        return redirect(request.META.get('HTTP_REFERER'))
                else:
                    messages.success(request, "Incorrect password, please try again")
                    return redirect(request.META.get('HTTP_REFERER'))
            except User.DoesNotExist:
                messages.success(request, "Unkown username, please try again")
                return redirect(request.META.get('HTTP_REFERER'))

        elif page=='add-user':
            [Group.objects.create(name=x) for x in dict(user_levels) if len(Group.objects.filter(name=x))==0]
            Username=request.POST["Username"]
            Fullname=str(request.POST["Fullname"])
            first, *last = Fullname.split()
            name1 = "{first}".format(first=first)
            name2 = "{last}".format(last=" ".join(last))
            Phone=request.POST["Phone"]
            Email=request.POST["Email"]
            Gender=request.POST["Gender"] 
            Password=str(request.POST["Password"])
            User_Level=request.POST["User_Level"]
            # first check if username exist
            if  User.objects.filter(username__iexact=Username).exists():
                return HttpResponse(json.dumps({'message':'Username already taken, suggest a valid one'}),content_type='application/json')
            elif User.objects.filter(email__iexact=Email).exists():
                return HttpResponse(json.dumps({'message':'Email already taken, suggest a valid one'}),content_type='application/json')
            else:
                # Save django user
                if User_Level in ['CEO','Medical Director','Finance Manager','Commercial Manager']:
                    user_obj = User.objects.create_superuser(username=Username,first_name=name1,
                        last_name=name2,email=Email,password=Password)
                else:
                    user_obj = User.objects.create_user(username=Username,first_name=name1,
                        last_name=name2,email=Email,password=Password)
                # attach group to the user
                user_obj.groups.add(Group.objects.get(name=User_Level))
                # add user to Our Custom User_Details Models
                User_Details.objects.create(User=user_obj,Gender=Gender,Contact=Phone)
                msg="Welcome %s, your account has been finalized"%(Username)
                return HttpResponse(json.dumps({'message':msg}),content_type='application/json')
             
        elif page=='change-password':
            old_password=request.POST['OldPassword']
            user_data=User.objects.get(username=request.user.username)
            test_pass=check_password(old_password,user_data.password)
            if test_pass: 
                user_data.set_password(request.POST['NewPasswordConfirm'])
                user_data.save()
                messages.success(request,'Password changed successfully')
                return redirect('/staff/logout')
            else:
                messages.success(request,'Password verificaation failed')
        elif page=='profile':
            username=request.POST['username']
            user_det=User_Details.objects.get(User__username=username)
            user_form=Staff_Form(request.POST,request.FILES,instance=user_det)
            if user_form.is_valid():
                commit_form=user_form.save(commit=False)
                commit_form.Gender=request.POST['gender']
                user_form.save()
                User.objects.filter(
                                username=username).update(
                                first_name=str(request.POST["first_name"]).title(),
                                last_name=str(request.POST["last_name"]).title(),
                                email=request.POST["email"])
                messages.success(request,'Changes saved, %s'%username)
            else:
                messages.success(request,'Error in form submission: %s'%user_form.errors)
        
        return redirect(request.META.get("HTTP_REFERER"))

def create_trans_id():
    transId=Journal_History_Checker.objects.all().values('Trans_Id').distinct().count() + 1
    transId=str(transId).zfill(3)
    return transId

@method_decorator(unauthenticated_staffs,name='get')
class OPD(View):
    
    def dispatch(self,  *args, **kwargs):
        return super(OPD,self).dispatch(*args, **kwargs)

    def get(self,request,*args,**kwargs):
        context={'page':'Registration','send_hbd':'Yes'}
        # check if page request is from appointment or messages
        try:
            kwargs['page']=int(kwargs['page'])
        except ValueError:
            pass

        if kwargs['page']=='dashboard':
            app_data=Appoitment.objects.all()
            pastApp=app_data.filter(Preferred_Date__lt=datetime.now())
            todayApp=app_data.filter(Preferred_Date=datetime.now())
            upcomingApp=app_data.filter(Preferred_Date__gt=datetime.now()).order_by('-Date')
            msg=Message.objects.all().order_by('-Date')
            context.update({'todayApp':todayApp,'tdApp':len(todayApp),'upcomingApp':upcomingApp,'tupApp':len(upcomingApp),
            'pastApp':pastApp,'tpastApp':len(pastApp),'msgRecieved':msg,'tmsgRec':len(msg)})
            return render(request,'I_CARE/admin/opd-dashboard.html',context)
        elif kwargs['page']=='app_mesg':
            app_data=Appoitment.objects.all()
            pastApp=app_data.filter(Preferred_Date__lt=datetime.now())
            todayApp=app_data.filter(Preferred_Date=datetime.now())
            upcomingApp=app_data.filter(Preferred_Date__gt=datetime.now()).order_by('-Date')
            msg=Message.objects.all().order_by('-Date')
            context.update({'todayApp':todayApp,'tdApp':len(todayApp),'upcomingApp':upcomingApp,'tupApp':len(upcomingApp),
            'pastApp':pastApp,'tpastApp':len(pastApp),'msgRecieved':msg,'tmsgRec':len(msg)})
            return render(request,'I_CARE/admin/opd-pat-app-mesg.html',context)
        elif kwargs['page']=='pat-reg' or isinstance(kwargs['page'],int) :
            # load appointment data 
            if kwargs['page'] !='pat-reg':
                app_data=Appoitment.objects.get(id=kwargs['page'])
                fullname = str(app_data.Name)
                first, *last = fullname.split()
                app_data={'first_name':"{first}".format(first=first),'surname':"{last}".format(last=" ".join(last)),
                        'tel':app_data.Phone}
                context.update(app_data)
            context.update({'form':Patients_Form()})
            return render(request,'I_CARE/admin/opd-pat-reg.html',context)
        elif kwargs['page']=='pat-update':
            context.update({'form':Patients_Form()})
            return render(request,'I_CARE/admin/opd-pat-update.html',context)
        elif kwargs['page']=='pat-complaints':
            return render(request,'I_CARE/admin/opd-complaints.html',context)
        elif kwargs['page']=='search-patient':
            pat_data=Patients.objects.get(Patient_Id=request.GET['Patient_Id'])
            if str(pat_data.Profile).__contains__('avatar'):
                img_data=str(pat_data.Profile)
            else:
                img_data=str(pat_data.Profile.url)
            insurance_name='None'
            if pat_data.Insurance_Type:
                insurance_name=pat_data.Insurance_Type.Name 
            info_data={'First_Name':pat_data.First_Name,'Surname':pat_data.Surname,
                    'DOB':str(pat_data.DOB),'Age':pat_data.Age,'Gender':pat_data.Gender,'Insurance_Id':pat_data.Insurance_Id,
                    'Residence':pat_data.Residence,'Nationality':pat_data.Nationality,'Insurance_Name':insurance_name,
                    'Profile':img_data,'Tel':pat_data.Tel,'Occupation':pat_data.Occupation,'Patient_Id':pat_data.Patient_Id,
                    'Last_Visit':str(datetime.strptime(str(pat_data.Last_Visit.date()),"%Y-%m-%d").strftime('%a, %d %b %Y')),
                    'Emergency_Tel':pat_data.Emergency_Tel,'Email':pat_data.Email}
            return HttpResponse(json.dumps({'pat_data':json.dumps(info_data)}),content_type='application/json')
       
    @transaction.atomic(using=None, savepoint=True, durable=True)
    def post(self,request,*args,**kwargs):
        # check if page request is from appointment or messages
        try:
            kwargs['page']=int(kwargs['page'])
        except ValueError:
            pass
        if kwargs['page']=='pat-reg' or isinstance(kwargs['page'],int):
            form = Patients_Form(request.POST,request.FILES)
            msg='Process initiated at the payment department...'
            if form.is_valid():
                procedure_list=request.POST.getlist('Procedure_Name')
                procedure_data=Procedures.objects.filter(id__in=procedure_list)
                totalCost=procedure_data.aggregate(sum=Sum('Charge'))['sum']
                totalCost= totalCost if totalCost else Decimal(0)
                referred_facility=request.POST['Referring_Facility'] or None
                patient_init_id=gen_pat_id()
                commit_form=form.save(commit=False)
                commit_form.Patient_Id=patient_init_id
                commit_form.Balance=-totalCost
                commit_form.Gender=request.POST['gender']
                commit_form.Date_Joined=datetime.now().date()
                commit_form.Last_Visit=timezone.now()
                form.save()
                Patients_Checker.objects.create(Patient_Id=patient_init_id)
                # check if patient been registered from appointment then update patient id
                if isinstance(kwargs['page'],int):
                    Appoitment.objects.filter(Phone=request.POST['Tel']).update(Patient_Id=patient_init_id)
                for data in procedure_data:
                    Vitals.objects.create(
                        Patient_Id=form.instance,
                        Procedure=data,
                        Referring_Facility=referred_facility,
                        Referred_Doctor=request.POST['Reffered_Doctor'],
                        Treatment_Amount=data.Charge,
                        Logger=Loged_User(request))
                  
                msg='Process initiated at the payment department...'
                # check referring facility if saved already or not
                saveFacility(referred_facility)
                sms=SMS()
                msg_bdy=sms.getWLM_MSG(request.POST['First_Name'])
                asyncio.run(sms.SEND_ALERT([request.POST['Tel']],msg_bdy))
                messages.success(request,msg)
            else:
                messages.success(request,'Error on form submission: %s'%(form.errors))
        elif kwargs['page']=='pat-update':
            form=Patients_Form(request.POST,request.FILES,instance=Patients.objects.get(Patient_Id=request.POST['searchPat'])) 
            if form.is_valid():
                commit_form=form.save(commit=False)
                commit_form.Gender=request.POST['gender']
                form.save()
                messages.success(request,'%s demo. updated successfully'%(request.POST['First_Name']))
            else:
                messages.success(request,'Error occured:%s'%form.errors)
        elif kwargs['page']=='pat-complaints':
            procedure_list=request.POST.getlist('Procedure_Name')
            procedure_data=Procedures.objects.filter(id__in=procedure_list)
            totalCost=procedure_data.aggregate(sum=Sum('Charge'))['sum']
            totalCost= totalCost if totalCost else Decimal(0)
            patData=Patients.objects.filter(Patient_Id=request.POST['searchPat'])
            patient_init_id=patData.first()
            referred_facility=request.POST['Referring_Facility'] or None
            # check procedures and apply bill to patient
            for data in procedure_data:
                Vitals.objects.create(
                    Patient_Id=patient_init_id,
                    Procedure=data,
                    Referring_Facility=referred_facility,
                    Referred_Doctor=request.POST['Reffered_Doctor'],
                    Treatment_Amount=data.Charge,
                    Logger=Loged_User(request))
            # update insurance details
            updatingFields={}
            if request.POST['Insurance_Id']:
                updatingFields['Insurance_Id']=request.POST['Insurance_Id']
            if request.POST['Insurance_Type']:
                updatingFields['Insurance_Type']=Insurance.objects.get(Name=request.POST['Insurance_Type'])
            # check if there is a field to update then apply update
            if updatingFields:
                patData.update(**updatingFields)
            patData.update(Balance=F('Balance')-totalCost)
           
            msg='Process initiated at the payment department...'
            # check referring facility if saved already or not
            saveFacility(referred_facility)
            messages.success(request,msg)
        elif kwargs['page']=='birthdays':
            crl_date=datetime.now()
            clr_day=crl_date.day
            clr_month=crl_date.month
            birthday_pat=Patients.objects.filter(DOB__day=clr_day,DOB__month=clr_month).exclude(Patient_Id__in=Birthday_Wishes.objects.filter(Due_Date=crl_date,Delivery_Status=True).values('Patient_Id__Patient_Id'))
            if birthday_pat:
                sms_init=SMS()
                for data in birthday_pat:
                    msg=f'Hello {data.First_Name}, people might see you as just a client to us, but in reality you mean much more than that to us. You are a friend, whom we care so much about. Happy Birthday!'
                    alert_res=asyncio.run(sms_init.SEND_ALERT([data.Tel],msg))
                    # check if sms is delivered then record to prevent sms repetitions
                    sms_dev_status=False
                    if isinstance(alert_res,dict):
                        if 'data' in alert_res:
                            sms_dev_status=True
                    obj, created = Birthday_Wishes.objects.get_or_create(
                                    Patient_Id=data,
                                    Due_Date=crl_date,
                                    defaults={'Message':msg,'New_Age':crl_date.year-data.DOB.year,
                                            'Delivery_Status':sms_dev_status,'Due_Date': crl_date},
                                )
                birthday_pat.update(Age=crl_date.year-F('DOB__year'))
            return HttpResponse(json.dumps({'message':'Birthday checks in progress...'}),content_type='application/json')
        return redirect(request.META.get('HTTP_REFERER'))

@method_decorator(unauthenticated_staffs,name='get')
@method_decorator(class_allow_users(allowed_levels=['CEO','Finance Manager','Receptionist','Secretary']),name='get')
class Payment_Department(View):
    
    def dispatch(self,  *args, **kwargs):
        return super(Payment_Department,self).dispatch(*args, **kwargs)

    def get(self,request,*args,**kwargs):
        context={'page':'Payment'}
        
        if kwargs['page']=='dashboard':
            app_data=Appoitment.objects.all()
            pastApp=app_data.filter(Preferred_Date__lt=datetime.now())
            todayApp=app_data.filter(Preferred_Date=datetime.now())
            upcomingApp=app_data.filter(Preferred_Date__gt=datetime.now()).order_by('-Date')
            msg=Message.objects.all().order_by('-Date')
            context.update({'todayApp':todayApp,'tdApp':len(todayApp),'upcomingApp':upcomingApp,'tupApp':len(upcomingApp),
            'pastApp':pastApp,'tpastApp':len(pastApp),'msgRecieved':msg,'tmsgRec':len(msg)})
            return render(request,'I_CARE/admin/service-dashboard.html',context)
        elif kwargs['page']=='pat-journal':
            # load patients journal 
            journal=(Vitals.objects.all().order_by('-Date','Treatment_Amount').annotate(Patient_Ref=F('Patient_Id__Patient_Id'),Balance=F('Treatment_Amount')-F('Paid_Amount'),Treatment_Name=Concat(F('Procedure__Procedure'),Value('-'),F('Procedure__Modality__Acronym'),output_field=CharField())).values())
            journal=json.dumps(list(journal), cls=DjangoJSONEncoder)
            # journal = serializers.serialize('json', journal)
            pat_data=Patients.objects.all().order_by('-Date_Joined','Balance')
            context.update({'journalData': journal,'pat_data':pat_data})
            return render(request,'I_CARE/admin/service-payment.html',context)
        
    @transaction.atomic(using=None, savepoint=True, durable=True)
    def post(self,request,*args,**kwargs):
       
        if kwargs['page']=='journal-payment':
            transID=create_trans_id()
            patientID=request.POST['Patient_Id']
            Amount=Decimal(request.POST['Amount'])
            jData=Vitals.objects.exclude(Paid_Amount=F('Treatment_Amount')).filter(Patient_Id__Patient_Id=patientID)
            for data in jData:
                # record payment history
                Journal_History.objects.create(
                    Payment_Journal = data,Paid_Amount = (data.Treatment_Amount-data.Paid_Amount),
                    Payment_Type=request.POST['Mode'], Approved_By=Loged_User(request),
                    Payment_Comment=request.POST['Comment'],Date=request.POST['PaymentDate']
                )
                data.Paid_Amount=F('Treatment_Amount')
                data.Department=data.Procedure.Tag
                data.Trans_Id=transID
            Vitals.objects.bulk_update(jData,['Paid_Amount','Department','Trans_Id'])
            Patients.objects.filter(Patient_Id=request.POST['Patient_Id']).update(Balance=F('Balance')+Amount)
            Journal_History_Checker.objects.create(Trans_Id=transID,Cashier=Loged_User(request))
            sms=SMS()
            msg_bdy=sms.getPAYMENT_MSG(request.POST['First_Name'])
            asyncio.run(sms.SEND_ALERT([request.POST['Tel']],msg_bdy))
            return HttpResponse(json.dumps({'message':'Payment recorded successfully','transID':transID}),content_type='application/json')
        elif kwargs['page']=='del-folder':
            Patients.objects.filter(Patient_Id=request.POST['Patient_Id']).delete()
            return HttpResponse(json.dumps({'message':request.POST['Name']}),content_type='application/json')
        
        return redirect(request.META.get('HTTP_REFERER'))

@method_decorator(unauthenticated_staffs,name='get')
@method_decorator(class_allow_users(allowed_levels=['CEO','Medical Director','Radiographer','Sonographer','Lab Scientist']),name='get')
class Imaging(View):
    
    def dispatch(self, request, *args, **kwargs):
        return super(Imaging,self).dispatch(request, *args, **kwargs)

    def get(self,request,*args,**kwargs):
        context={'page':'Imaging Department',
                'scan_types':Procedures.objects.filter(Tag='Radiology')}
        if kwargs['page']=='test':
            return render(request,'I_CARE/admin/radiology-test.html',context)
        else:
            return redirect(request.META.get('HTTP_REFERER'))
            
    @transaction.atomic(using=None, savepoint=True, durable=True)
    def post(self,request,*args,**kwargs):
         
        if kwargs['page']=='test':
            vitData=Vitals.objects.get(id=request.POST['Vital_Id'])
            patData=vitData.Patient_Id
            # record complaints
            msg='Completed'
            file = request.FILES.get('Docs', None)
            if file:
                Presenting_Complaints.objects.create(
                    Patient_Id= patData,Complaint_Category=request.POST['procedure_name'],
                    Complaint_Type='RADIOLOGY',Complaints = request.POST['Complaints'],
                    Tech_Instance=Loged_User_Instance(request),
                    Tech_Report=file,Tech_Report_Name=file.name,
                    Vitals=vitData
                )
                vitData.Department='Consultation'
                vitData.Status='Waiting'
                msg='Test recorded and pushed to radiologist'
            else:
                Presenting_Complaints.objects.create(
                    Patient_Id= patData,Complaint_Category=request.POST['procedure_name'],
                    Complaint_Type='RADIOLOGY',Complaints = request.POST['Complaints'],
                    Tech_Instance=Loged_User_Instance(request),
                    Vitals=vitData
                )
                vitData.Status='Done'
                msg='Test recorded successfully'
            # save status 
            vitData.save()
            messages.success(request,msg)
            return redirect(request.META.get('HTTP_REFERER'))
        
@method_decorator(unauthenticated_staffs,name='get')
@method_decorator(class_allow_users(allowed_levels=['CEO','Medical Director','Lab Scientist']),name='get')
class Laboratory(View):

    def dispatch(self, request, *args, **kwargs):
        return super(Laboratory,self).dispatch(request, *args, **kwargs)

    def get(self,request,*args,**kwargs):
        context={'page':'Laboratory Department'}
        if kwargs['page']=='test':
            return render(request,'I_CARE/admin/lab-test.html',context)
        else:
            return redirect(request.META.get('HTTP_REFERER'))
            
    @transaction.atomic(using=None, savepoint=True, durable=True)
    def post(self,request,*args,**kwargs):
         
        if kwargs['page']=='test':
            pat_data=Patients.objects.get(Patient_Id=request.POST['Patient_Id'])
            # record complaints
            Presenting_Complaints.objects.create(
                Patient_Id= pat_data,Complaint_Category='Laboratory',
                Complaint_Type='LAB TEST',Complaints = request.POST['Complaints'],
                Logger_Instance=Loged_User_Instance(request)
            )
            messages.success(request,'Test recorded and pushed to doctor for review')
            
            return redirect(request.META.get('HTTP_REFERER'))

@method_decorator(unauthenticated_staffs,name='get')
@method_decorator(class_allow_users(allowed_levels=['CEO','Medical Director','Radiographer','Sonographer']),name='get')
class Doctors(View):

    def dispatch(self,  *args, **kwargs):
        return super(Doctors,self).dispatch(*args, **kwargs)

    def get(self,request,*args,**kwargs):
        context={'page':'Doctors Page'}
        if kwargs['page']=='consulting':
            return render(request,"I_CARE/admin/doc-consultation.html",context)
       
    @transaction.atomic(using=None, savepoint=True, durable=True)
    def post(self,request,*args,**kwargs):

        if kwargs['page']=='approve-test':
            vit_data=Vitals.objects.get(id=request.POST['Vital_Id'])
            # pat_data=vit_data.Patient_Id
            presHist=Presenting_Complaints.objects.get(Vitals=vit_data)
            # update presHist
            file = request.FILES['Report']
            presHist.Docs_Complaints=request.POST['Docs_Complaints']
            presHist.Docs_Instance=Loged_User_Instance(request)
            presHist.Docs_Report=file
            presHist.Docs_Report_Name=file.name
            presHist.save()
            
            # Update vitals Department to Consultation and Status to Waiting so if patient is doing double procedures
            # that one will be of from the table
            procedure_data=Procedures.objects.get(id=vit_data.Procedure.id)
            vit_data.Status='Reviewed'
            vit_data.Department=procedure_data.Tag
            vit_data.save()
            messages.success(request,'Report approved and available to print')
            return redirect(request.META.get('HTTP_REFERER'))
        
class Requisition_Form(View):

    def dispatch(self,  *args, **kwargs):
        return super(Requisition_Form,self).dispatch(*args, **kwargs)

    def get(self,request,*args,**kwargs):
        context={'page':'Requisition'}
        if kwargs['page']=='place-request':
            reqHist=Requisition.objects.filter(Placeholder=User_Details.objects.get(User=request.user))
            context.update({'reqHist':reqHist})
            return render(request,'I_CARE/admin/requisition-form.html',context)
        elif kwargs['page']=='pending-request':
            reqHist=Requisition.objects.filter(Approval_Authority__Authorizer=User_Details.objects.get(User=request.user))
            context.update({'reqHist':reqHist})
            return render(request,'I_CARE/admin/pending-requisition.html',context)
    
    @transaction.atomic(using=None, savepoint=True, durable=True)
    def post(self,request,*args,**kwargs):
        if kwargs['page']=='place-request':
            total_cost=(Decimal(request.POST['Total_Cost']))
            authorizer=Approval_Authority.objects.filter(Q(Min_Amount__lte=total_cost) & Q(Max_Amount__gte=total_cost)).first()
            if authorizer:
                Requisition.objects.create(
                    Placeholder=User_Details.objects.get(User=request.user),
                    Description=request.POST['Description'],
                    Delivery_Timeline=str(request.POST['Delivery_Tm']).title(),
                    Quantity=request.POST['Quantity'],
                    Price=request.POST['Price'],
                    Total_Cost=request.POST['Total_Cost'],
                    Approval_Authority=authorizer,
                )
                messages.success(request,'Request placed successful')
            else:
                messages.success(request,'Your request is above limit')
        elif kwargs['page']=='pending-request':
            total_cost=(Decimal(request.POST['Total_Cost']))
            authorizer=Approval_Authority.objects.filter(Q(Min_Amount__lte=total_cost) & Q(Max_Amount__gte=total_cost)).first()
            if authorizer:
                Requisition.objects.filter(id=request.POST['Request_Id']).update(
                    Description=request.POST['Description'],
                    Delivery_Timeline=str(request.POST['Delivery_Tm']).title(),
                    Quantity=request.POST['Quantity'],
                    Price=request.POST['Price'],
                    Total_Cost=request.POST['Total_Cost'],
                    Approval_Authority=authorizer,
                )
                messages.success(request,'Request update successful')
            else:
                messages.success(request,'Your request is above limit')
        elif kwargs['page']=='alter-request':
            Requisition.objects.filter(id=request.POST['requestID']).update(
                Approval_Status=request.POST['newStaus']
            )
            messages.success(request,'Request processed successfully')
        return redirect(request.META.get('HTTP_REFERER'))

@method_decorator(unauthenticated_staffs,name='get')
@method_decorator(class_allow_users(allowed_levels=['CEO','Medical Director','Radiographer','Sonographer','Lab Scientist','Nurse']),name='get')
class General_Reports(View):
    
    def dispatch(self, request, *args, **kwargs):
        return super(General_Reports,self).dispatch(request, *args, **kwargs)

    def get(self,request,*args,**kwargs):

        if kwargs['page']=='test':
            if kwargs['type']=='report-history':
                vitalHist=Presenting_Complaints.objects.all().order_by('-Date')
                context={'page':'Test Reports','vitalHist':vitalHist}
                return render(request,'I_CARE/admin/approved-reports.html',context)
        elif kwargs['page']=='receipt':
            transID=kwargs['type']
            jnrData=Journal_History.objects.filter(Payment_Journal__Trans_Id=transID)
            paymentData=jnrData.first()
            patData=paymentData.Payment_Journal.Patient_Id
            totalCost=jnrData.aggregate(sum=Sum('Payment_Journal__Treatment_Amount'))['sum']
            totalCost=totalCost if totalCost else Decimal(0)
            totalPaid=jnrData.aggregate(sum=Sum('Paid_Amount'))['sum']
            totalPaid=totalPaid if totalPaid else Decimal(0)
            totalBalance=totalCost-totalPaid
            context={'patData':patData,'jnrData':jnrData,'totalCost':totalCost,'totalPaid':totalPaid,
                     'totalBalance':totalBalance,'paymentData':paymentData,'invoce_id':transID}
            return render(request,'I_CARE/admin/invoice.html',context)
        else:
            return redirect(request.META.get('HTTP_REFERER'))
            
@method_decorator(unauthenticated_staffs,name='get')
@method_decorator(class_allow_users(allowed_levels=['CEO','Medical Director','Pharmacist']),name='get')
class Pharmacy(View):
    context={'page':'Pharmacy'}

    def GenID(self):
        count = Stocks_Checker.objects.values('Product_Id').distinct().count() + 1
        Product_Id = "%s%s"%("P",str(count).zfill(3))
        return Product_Id

    def dispatch(self, request, *args, **kwargs):
        sales_data=Drugs_Prescriptions.objects.exclude(Sales_Status__in=['Pending','Denied']).filter(Date=datetime.now())

        tdSales=sales_data.aggregate(sum=Sum('Cost'))['sum']
        tdSales=tdSales if tdSales else Decimal(0)

        tdPaid=sales_data.aggregate(sum=Sum('Amount_Paid'))['sum']
        tdPaid=tdPaid if tdPaid else Decimal(0)
        
        tdBalance=tdSales-tdPaid

        self.context.update({
            'total_sales':tdSales,
            'total_paid':tdPaid,
            'balance':tdBalance,
            'total_pres':len(sales_data)
        })
         
        return super(Pharmacy, self).dispatch(request, *args, **kwargs)

    def get(self,request, *args, **kwargs):
        
        if kwargs['page'] =='dashboard':
            return render(request,'I_CARE/admin/pharm-dashbord.html',self.context) 
        elif kwargs['page'] =='stocking':
            stock_form=Stocks_Form()
            departments=Stocks_Department.objects.all()
            supplier=Supplier.objects.all()
            # 
            stocks_list = Stocks.objects.all().order_by('Product_Name').values()
            self.context.update({"form": stock_form,'departmentList':departments,'supplierList':supplier,
            'items': stocks_list,'jsonDrugs':json.dumps(list(stocks_list),cls=DecimalEncoder)})
            
            return render(request,'I_CARE/admin/pharm-drug-stocking.html', self.context)
        elif kwargs['page'] =='list':
            stocks_list = Stocks.objects.all().order_by('Product_Name')
            total_items=stocks_list.aggregate(sum=Sum('Quantity'))['sum']
            total_items=total_items if total_items else 0
            self.context.update({'items': stocks_list,"items_size":len(stocks_list),
            "total_items":total_items})
            return render(request,'I_CARE/admin/pharm-drug-list.html', self.context)
        elif kwargs['page']=='cash-form':
            stocks_list = Stocks.objects.all().order_by('Product_Name')
            self.context.update({'stocks_list':stocks_list})
            return render(request,'I_CARE/admin/pharm-cash-form.html',self.context)
       
        elif kwargs['page'] in ['available-stocks','low-stocks']:
            stocks_type=None
            sales_data=Stocks.objects.order_by('Product_Name').annotate(on_retail=ExpressionWrapper(F('Quantity')*F('Retail'),output_field=DecimalField()),on_wholesale=ExpressionWrapper(F('Quantity')*F('Whole_Sale'),output_field=DecimalField()))
            if  kwargs['page'] == 'available-stocks':
                sales_data=sales_data.filter(Quantity__gt=0)
                stocks_type='AVAILABLE STOCKS'
            else:
                sales_data=sales_data.filter(Quantity=0)
                stocks_type='LOW/OUT STOCKS'
            total_ret=sales_data.aggregate(sum=Sum('on_retail'))['sum']
            total_whosales=sales_data.aggregate(sum=Sum('on_wholesale'))['sum']

            context={'items':sales_data,'stocks_type':stocks_type,
            'total_ret':total_ret,'total_whosales':total_whosales}
            return render(request,'I_CARE/admin/stocks-report.html',context)
        elif kwargs['page']=='purchased-stocks':
            date_from=datetime.strptime(request.GET['Date_From'],'%Y-%m-%d').date()
            date_to=datetime.strptime(request.GET['Date_To'],'%Y-%m-%d').date()
            sales_data=New_Stocks.objects.order_by('Date').filter(Date__range=[date_from,date_to])
            total_sales=sales_data.aggregate(sum=Sum('Total'))['sum']
            total_sales=total_sales if total_sales else 0.00
            context={'items':sales_data,'date_from':date_from,'date_to':date_to,
            'total_purchase':total_sales}
            return render(request,'I_CARE/admin/stocks-purchased-report.html',context)
        elif kwargs['page']=='sales-report':
            sales_type=request.GET['sales_type']
            date_from=datetime.strptime(request.GET['Date_From'],'%Y-%m-%d').date()
            date_to=datetime.strptime(request.GET['Date_To'],'%Y-%m-%d').date()
            sales_data=Drugs_Prescriptions.objects.order_by('Date').exclude(Sales_Status__in=['Pending','Denied']).filter(Date__range=[date_from,date_to])
            
            if sales_type=='Daily Sales':
                sales_data=sales_data.filter(Cost=F('Amount_Paid'))
            else:
                sales_data=sales_data.filter(Cost__gt=F('Amount_Paid'))

            total_sales=sales_data.aggregate(sum=Sum('Cost'))['sum']
            total_sales=total_sales if total_sales else Decimal(0.00)

            total_paid=sales_data.aggregate(sum=Sum('Amount_Paid'))['sum']
            total_paid=total_paid if total_paid else Decimal(0.00)

            balance=total_sales-total_paid

            context={'items':sales_data,'date_from':date_from,'date_to':date_to,
            'total_sales':total_sales,'total_paid':total_paid,'balance':balance,
            'sales_type':str(sales_type).upper()}
            return render(request,'I_CARE/admin/sales-report.html',context)
    
    @transaction.atomic(using=None, savepoint=True)
    def post(self,request,*args,  **kwargs):
        if kwargs['page'] =='stocking':
            self.stocking_tab='stocking'
            # update if product id exist
            try:
                stock_data=Stocks.objects.get(Product_Id=request.POST['Product_Id'])
                oldQty=stock_data.Quantity
                newQty=oldQty+int(request.POST["Quantity"])
                stock_form=Stocks_Form(request.POST,instance=stock_data)
                if stock_form.is_valid():
                    Rprofit=Decimal(stock_form.cleaned_data["Retail"])-Decimal(stock_form.cleaned_data["Purchase"])
                    Wprofit=Decimal(stock_form.cleaned_data["Whole_Sale"])-Decimal(stock_form.cleaned_data["Purchase"])
                    commit_form = stock_form.save(commit=False)
                    commit_form.Quantity=newQty
                    commit_form.Total=newQty*Decimal(stock_form.cleaned_data["Purchase"])
                    commit_form.Rprofit=Rprofit
                    commit_form.Wprofit=Wprofit
                    stock_form.save()
                    
                    # record new stock if qty > 0
                    if int(stock_form.cleaned_data["Quantity"])>0:
                        New_Stocks.objects.create(
                            Product_Id = stock_form.cleaned_data["Product_Id"],
                            Product_Name = stock_form.cleaned_data["Product_Name"],
                            Department = stock_form.cleaned_data["Department"],
                            Quantity = stock_form.cleaned_data["Quantity"],
                            Vat = stock_form.cleaned_data["Vat"],
                            Retail =Decimal(stock_form.cleaned_data["Retail"]),
                            Whole_Sale =Decimal(stock_form.cleaned_data["Whole_Sale"]),
                            Purchase = stock_form.cleaned_data["Purchase"],
                            Total = stock_form.cleaned_data["Total"],
                            Rprofit = Rprofit,
                            Wprofit = Rprofit,
                            # supplier details
                            Suppliers = stock_form.cleaned_data["Suppliers"],
                            Invoice = stock_form.cleaned_data["Invoice"]
                        )

                    messages.success(request, "Product updated successfully")
                else:
                    messages.success(request, "Error in form: %s"%stock_form.errors)
            except Stocks.DoesNotExist:
                stock_form=Stocks_Form(request.POST)
                if stock_form.is_valid():
                    Rprofit=Decimal(stock_form.cleaned_data["Retail"])-Decimal(stock_form.cleaned_data["Purchase"])
                    Wprofit=Decimal(stock_form.cleaned_data["Whole_Sale"])-Decimal(stock_form.cleaned_data["Purchase"])
                    gen_product_id=self.GenID()
                    commit_form = stock_form.save(commit=False)
                    commit_form.Product_Id=gen_product_id
                    commit_form.Rprofit=Rprofit
                    commit_form.Wprofit=Wprofit
                    # commit_form.Retail=Decimal(request.POST["total_r_price"])
                    # commit_form.Whole_Sale=Decimal(request.POST["total_w_price"])
                    stock_form.save()
                    Stocks_Checker.objects.create(Product_Id=gen_product_id,Product_Name=stock_form.cleaned_data["Product_Name"])
                    
                    New_Stocks.objects.create(
                        Product_Id = gen_product_id,
                        Product_Name = stock_form.cleaned_data["Product_Name"],
                        Department = stock_form.cleaned_data["Department"],
                        Quantity = stock_form.cleaned_data["Quantity"],
                        Vat = stock_form.cleaned_data["Vat"],
                        Retail =Decimal(stock_form.cleaned_data["Retail"]),
                        Whole_Sale =Decimal(stock_form.cleaned_data["Whole_Sale"]),
                        Purchase = stock_form.cleaned_data["Purchase"],
                        Total = stock_form.cleaned_data["Total"],
                        Rprofit = Rprofit,
                        Wprofit = Rprofit,
                        # supplier details
                        Suppliers = stock_form.cleaned_data["Suppliers"],
                        Invoice = stock_form.cleaned_data["Invoice"]
                    )

                    messages.success(request, "New product added successfully")
                    return redirect('/pharm/stocking')
                else:
                    messages.success(request, "Error in form: %s"%stock_form.errors)
        elif kwargs['page']=='sales-form':
            amount_paying=Decimal(request.POST['Amount_Paid'])
            # net_cost=Decimal(request.POST['Cost'])
            # bill_bal=Decimal(request.POST['Balance'])
            # office_payment=Decimal(request.POST['Office_Payment'])

            # first check if patient id exist else create General Patient account for the transaction
            pat_data,patDataCreated=Patients.objects.get_or_create(Patient_Id=request.POST['Patient_Id'],
            defaults={
                'First_Name':'General',
                'Surname' :'Patient',
                'Age': 1,'Gender':'Male',
                'Residence':'None',
                'Nationality':'Ghanaian',
                'Tel':'xxx-xxxx-xxx-xxx',
                'Occupation':'None',
                'Date_Joined':datetime.now(),
                'Balance':0
            })
            # first get all items with none journal data and attach journal to them
            items=request.POST.getlist('Items[]')
            bkrm2=BulkCreateManager()
            newItemsCost=0
            for index,data in enumerate(items):
                if data:
                    presData=json.loads(data)
                    if presData['Journal_ID'] =='None':
                        # create or get journal for these items and attache journal to them
                        jrnObj,create=Payment_Journal.objects.get_or_create(
                        Date=datetime.now(),Patient_Id=pat_data,Treatment_Name = 'Pharmacy',
                        defaults={'Treatment_Amount':0,'Logger_Instance':Loged_User_Instance(request)})
                        # 
                        bkrm2.add(Drugs_Prescriptions(
                            Patient_Id= pat_data,
                            Drug_Id= Stocks.objects.get(Product_Id=presData['ID']),
                            Quantity=presData['Quantity'],
                            Price=presData['Retail'],
                            Cost=presData['Cost'],
                            Frequency = 'None',
                            Start_Date=datetime.now(),
                            End_Date=datetime.now(),
                            Logger_Instance=Loged_User_Instance(request),
                            Journal_Id=jrnObj))
                        # attach journal to item
                        presData['Journal_ID']=jrnObj.pk
                        dumpsData=json.dumps(presData)
                        items[index]=dumpsData
                        jrnObj.Treatment_Amount=jrnObj.Treatment_Amount+Decimal(presData['Cost'])
                        jrnObj.save()
                        newItemsCost+=Decimal(presData['Cost'])
            bkrm2.done()
            # now apply amount paying if there's any 
            amount_okay=0
            for index,data in enumerate(items):
                if data:
                    sales_data=json.loads(data) 
                    # print(sales_data,'\n---------------')
                    cart_data=Drugs_Prescriptions.objects.filter(Drug_Id__Product_Id=sales_data['ID'],Journal_Id__id=sales_data['Journal_ID'],Sales_Status='Pending').exclude(Cost=F('Amount_Paid')).order_by('Cost')
                    for data in cart_data:
                        item_paying_amount=Decimal(data.Cost)-Decimal(data.Amount_Paid)
                        if amount_paying<item_paying_amount:
                            item_paying_amount=amount_paying
                        data.Amount_Paid=Decimal(data.Amount_Paid)+item_paying_amount
                        data.Sales_Status='Sold'
                        # reduce stock quantity and balance the total cost 
                        drug_data=data.Drug_Id
                        newQty=drug_data.Quantity-data.Quantity
                        drug_data.Quantity=newQty
                        drug_data.Total=newQty*drug_data.Purchase
                        drug_data.save()
                        # reduce items_paid_bal per item update
                        amount_paying-=item_paying_amount
                        amount_okay+=item_paying_amount
                        # update the payment journal record
                        Payment_Journal.objects.filter(id=sales_data['Journal_ID']).update(Paid_Amount=F('Paid_Amount')+item_paying_amount)
                    Drugs_Prescriptions.objects.bulk_update(cart_data,['Amount_Paid','Sales_Status'])
            
            # get any pending drugs from patients drugs_prescription history
            # and set Sales status to Purchase Denied and unbill the cost from patient account
            notAffordDrugs=Drugs_Prescriptions.objects.filter(Patient_Id=pat_data,Sales_Status='Pending').order_by('Cost')
            totalNotAffordDrugs=notAffordDrugs.aggregate(sum=Sum('Cost'))['sum']
            totalNotAffordDrugs=totalNotAffordDrugs if totalNotAffordDrugs else Decimal(0)
            # now update the journal
            for data in notAffordDrugs:
                jrn_data=data.Journal_Id
                jrn_data.Treatment_Amount-=data.Cost
                jrn_data.save()
                # update sales status of the item
                data.Sales_Status='Denied'
            Drugs_Prescriptions.objects.bulk_update(notAffordDrugs,['Sales_Status'])
            pat_data.Balance=(pat_data.Balance-newItemsCost)+(totalNotAffordDrugs+amount_okay)
            pat_data.save()
            return HttpResponse(json.dumps({'message':'data received'}),content_type='application/json')
        elif kwargs['page']=='new_department':
            msg=None
            try:
                Stocks_Department.objects.create(Name=str(request.POST['Department']).upper())
                msg='Department added successfully'
            except IntegrityError:
                msg='Department already exist'
            return HttpResponse(json.dumps({'message':msg}),content_type='application/json')
        elif kwargs['page']=='add_supplier':
            msg=None
            try:
                Supplier.objects.create(
                    Contact=request.POST["contact"],
                    Company_Name=str(request.POST["company_name"]).upper(),
                    Address=request.POST["address"],
                )
                msg='Supplier added successfully'
            except IntegrityError:
                msg='Supplier already exist'
            return HttpResponse(json.dumps({'message':msg}),content_type='application/json')
        elif kwargs['page']=='delete':
            self.stocking_tab='list'
            Stocks.objects.filter(Product_Id=request.POST['Id']).delete()
            return HttpResponse(json.dumps({'message':f"{request.POST['Name']} deleted successfully"}),content_type='application/json')
        return redirect(request.META.get('HTTP_REFERER'))

# web 
class Home_Page(View):
    
    def dispatch(self,  *args, **kwargs):
        return super(Home_Page,self).dispatch(*args, **kwargs)

    def get(self,request):
        return render(request,"I_CARE/web/index.html",{'page':'web'})

class Home_Page_Links(View):
    
    def dispatch(self,  *args, **kwargs):
        return super(Home_Page_Links,self).dispatch(*args, **kwargs)

    def get(self,request,*args, **kwargs):
        if kwargs['page']=="contact-us":
            return render(request,"I_CARE/web/contact-us.html",{'page':kwargs['page']})
        elif kwargs['page']=="our-services":
            return render(request,"I_CARE/web/our-services.html",{'page':kwargs['page']})
        elif kwargs['page']=="about-us":
            return render(request,"I_CARE/web/about-us.html",{'page':kwargs['page']})
        elif kwargs['page']=='patients-data':
            load_data=request.GET['load']
            context={}
            if load_data=='consultation':
                vitalWaiting=Vitals.objects.filter(Department='Consultation',Status='Waiting')
                # # doctors complaints records
                pc_hist=Presenting_Complaints.objects.exclude(Vitals__Department='Radiology').filter(Patient_Id__Patient_Id__in=vitalWaiting.values('Patient_Id__Patient_Id')).order_by('-Date').annotate(Patient_ID=F('Patient_Id__Patient_Id'),Technician=Concat(F('Tech_Instance__User__first_name'),Value(' '),F("Tech_Instance__User__last_name"),output_field=CharField()),Tech_Report_Url=Concat(Value('/media/'), 'Tech_Report',output_field=CharField()),
                    Doctor=Concat(F('Docs_Instance__User__first_name'),Value(' '),F("Docs_Instance__User__last_name"),output_field=CharField()),Docs_Report_Url=Concat(Value('/media/'), 'Docs_Report',output_field=CharField()),Vital_ID=F('Vitals__id')).values()
                pc_hist=list(pc_hist)
                
                # vitals
                vitalHist=vitalWaiting.annotate(Patient_ID=F('Patient_Id__Patient_Id'),Balance=F('Patient_Id__Balance'),Age=F('Patient_Id__Age'),Last_Seen=Cast('Patient_Id__Last_Visit', output_field=DateField()),
                    Fullname=Concat(F('Patient_Id__First_Name'),Value(' '),F("Patient_Id__Surname"),output_field=CharField()),Profile=F('Patient_Id__Profile'),First_Name=F('Patient_Id__First_Name'),
                    Surname=F('Patient_Id__Surname'),Procedure_Name=Concat(F('Procedure__Procedure'),Value('-'),F('Procedure__Modality__Acronym')),Modality=F('Procedure__Modality__Modality')).values()
                vitalHist=list(vitalHist)

                context.update({'total_incoming':f'Active Patients({len(vitalHist)})',
                        'vitalHist':vitalHist,'pc_hist':pc_hist})

            elif load_data in ['laboratory','radiology']:
                vitalHist=Vitals.objects.filter(Department__in=['Laboratory','Radiology'],Status='Waiting')
                if load_data=='laboratory':
                    vitalHist=vitalHist.filter(Department='Laboratory')
                else:
                    vitalHist=vitalHist.filter(Department='Radiology')

                # doctors complaints records 
                pc_hist=Presenting_Complaints.objects.filter(Patient_Id__Patient_Id__in=vitalHist.values('Patient_Id__Patient_Id')).order_by('-Date').annotate(Patient_ID=F('Patient_Id__Patient_Id'),Technician=Concat(F('Tech_Instance__User__first_name'),Value(' '),F("Tech_Instance__User__last_name"),output_field=CharField()),Tech_Report_Url=Concat(Value('/media/'), 'Tech_Report',output_field=CharField()),
                    Doctor=Concat(F('Docs_Instance__User__first_name'),Value(' '),F("Docs_Instance__User__last_name"),output_field=CharField()),Docs_Report_Url=Concat(Value('/media/'), 'Docs_Report',output_field=CharField()),
                    Vital_ID=F('Vitals__id')).values()
                pc_hist=list(pc_hist)

                # vitals
                vitalHist=vitalHist.annotate(Patient_ID=F('Patient_Id__Patient_Id'),Balance=F('Patient_Id__Balance'),Age=F('Patient_Id__Age'),Last_Seen=Cast('Patient_Id__Last_Visit', output_field=DateField()),
                    Fullname=Concat(F('Patient_Id__First_Name'),Value(' '),F("Patient_Id__Surname"),output_field=CharField()),Profile=F('Patient_Id__Profile'),First_Name=F('Patient_Id__First_Name'),
                    Surname=F('Patient_Id__Surname'),Procedure_Name=Concat(F('Procedure__Procedure'),Value('-'),F('Procedure__Modality__Acronym')),Modality=F('Procedure__Modality__Modality')).values()
                vitalHist=list(vitalHist)

                context.update({'total_incoming':f'{len(vitalHist)} Patients waiting',
                                'pc_hist':pc_hist,'vitalHist':vitalHist})
            
            elif load_data=='pharmacy':
                incoming_patient=Patients.objects.all()
                incoming_patient_list=list(incoming_patient.annotate(Patient_ID=F('Patient_Id'),Fullname=Concat(F('First_Name'),Value(' '),F("Surname"),output_field=CharField())).values())
                # drugs prescriptions records
                prescHist=Drugs_Prescriptions.objects.filter(Sales_Status="Pending",Patient_Id__Patient_Id__in=incoming_patient.values('Patient_Id')).order_by('-Date').annotate(Journal_ID=F('Journal_Id__id'),Patient_ID=F('Patient_Id__Patient_Id'),Product_Id=F('Drug_Id__Product_Id'),Drug_Name=F('Drug_Id__Product_Name'),Doctor=Concat(F('Logger_Instance__User__first_name'),Value(' '),F("Logger_Instance__User__last_name"),output_field=CharField())).values()
                prescHist=list(prescHist)
                
                context.update({'waiting_list':incoming_patient_list,'prescHist':prescHist,
                'total_incoming':f'{len(incoming_patient)} Patients available...'})

            return HttpResponse(json.dumps(context,cls=DecimalEncoder))
        else:
            return render(request,"I_CARE/web/error-444.html",{'page':kwargs['page']})

    @transaction.atomic(using=None, savepoint=True)
    def post(self,request,*args,**kwargs):
    
        if kwargs['page']=='add-insurance':
            try:
                Insurance.objects.create(Name=request.POST['Name'])
                msg='Insurance added successfully...'
            except IntegrityError:
                msg='Insurance already exist, try something new'

            return HttpResponse(json.dumps({'message':msg}),content_type='application/json')
        elif kwargs['page']=="our-services":
            Appoitment.objects.create(
                Name=request.POST['name'],Phone=request.POST['phone'],
                Email=request.POST['email'],
                Preferred_Date=datetime.strptime(request.POST['date'],'%Y-%m-%d'),
                Message =request.POST['message'],
                Preferred_Time=request.POST['preferred_time']
            )
            # fullname = str(request.POST["name"])
            # first, *last = fullname.split()
            # name1 = "{first}".format(first=first)
            messages.success(request,'Hi there, your appointment has been noted. Thank You')
        elif kwargs['page']=="message":
            Message.objects.create(
                Name=request.POST['name'],Phone=request.POST['phone'],
                Email=request.POST['email'],
                Message = request.POST['message'],
            )
            fullname = str(request.POST["name"])
            first, *last = fullname.split()
            name1 = "{first}".format(first=first)
            msg='Hi %s, We will reply to your message shortly. Thank You'%(name1)
            messages.success(request,msg)
        elif kwargs['page']=="delete-app-msg":
            if request.POST['Type']=='App':
                Appoitment.objects.filter(id=request.POST['Id']).delete()
                return HttpResponse(json.dumps({'message':'Appointment cancelled successfully'}),content_type='application/json')
            else:
                Message.objects.filter(id=request.POST['Id']).delete()
                return HttpResponse(json.dumps({'message':'Message discarded successfully'}),content_type='application/json')
        return redirect(request.META.get('HTTP_REFERER'))
