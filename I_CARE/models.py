from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
import os,sys
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from django.db.models import F
# Create your models here.

def valid_extension(_img):
    if '.jpg' in _img:
        return "JPEG"
    elif '.jpeg' in _img:
        return "JPEG"
    elif '.png' in _img:
        return "PNG"

def compress_images(uploadedImage,width=200,height=200,format='JPEG'):
    lower_format=str(format).lower()
    try:
        imageTemproary = Image.open(uploadedImage)
        imageTemproary = imageTemproary.resize((width, height))
        if format in ['JPEG','jpeg','Jpeg','JPG','Jpg','jpg']:
            imageTemproary = imageTemproary.convert('RGB')
        outputIoStream = BytesIO()
        outputIoStream.seek(0)
        imageTemproary.save(outputIoStream, format=f'{format}', quality=95)
        uploadedImage = InMemoryUploadedFile(outputIoStream, 'ImageField',f'{uploadedImage.name.split(".")[0]}.{lower_format}',f'image/{lower_format}', sys.getsizeof(outputIoStream), None)
    except:
        uploadedImage =uploadedImage
    return uploadedImage

def default_static_image_path():
    return "/static/admin/assets/img/profiles/avatar.png"

def patients_profile_path(instance, filename):
    path = 'patients/{0}/{1}'.format(instance.Patient_Id, filename)
    return str(path)

def patients_docs_path(instance, filename):
    path = 'patients/{0}/docs/{1}'.format(instance.Patient_Id, filename)
    return str(path)

def user_profile_path(instance, filename):
    # filename='profile.%s'%filename.split(".")[1]
    path = 'staff/{0}/{1}'.format(instance.User.id, filename)
    return str(path)

def business_file_path(instance, filename):
    path = f'business/files/{filename}'
    return str(path)

class Business_Info (models.Model):
    Bus_Name=models.CharField(max_length=100,null=True,default='FRAMADA DENTAL CLINIC')
    Bus_Name_Abbr=models.CharField(max_length=100,null=True,default='FRAMADA')
    GPS_Address=models.TextField(default='AG-26572-2726, SANTASI-KUMASI')
    City=models.CharField(max_length=100,null=True,default='GH-Kumasi')
    Postal=models.CharField(max_length=50,null=True,default='P.O.BOX 9981 ADUM-KSM')
    App_Tel=models.CharField(max_length=15,default='+233')
    Gen_Tel=models.CharField(max_length=30,default='+233')
    Email=models.CharField(max_length=100,default='info@framadadentalclinic.com')
    Facebook=models.URLField(default='https://fb.com')
    Instagram=models.URLField(default='https://instagram.com')
    Linkedin=models.URLField(default='https://linkedin.com')
    Twitter=models.URLField(default='https://twitter.com')
    Youtube=models.URLField(default='https://youtube.com')
    Website=models.URLField(default='https://framada.pythonanywhere.com')
    Sms_Api_Key=models.CharField(max_length=200,default='OkZRZlp1T2lBMHdPQnQ5YVc=')
    Web_Logo = models.ImageField(default="Logo",null=True, blank=True, upload_to=business_file_path)
    Footer_Logo = models.ImageField(default="Logo",null=True, blank=True, upload_to=business_file_path)
    Fav_Icon = models.ImageField(default="Logo",null=True, blank=True, upload_to=business_file_path)

    class Meta:
        db_table='business_info'
        verbose_name='Business Detail'

    def __str__(self) -> str:
        return f'{self.Bus_Name}-{self.City}'
    
    def save(self, *args, **kwargs):
        self.Web_Logo=compress_images(self.Web_Logo,201,52,'PNG')
        self.Footer_Logo=compress_images(self.Footer_Logo,201,52,'PNG')
        self.Fav_Icon=compress_images(self.Fav_Icon,48,48,'PNG')
        super(Business_Info, self).save(*args, **kwargs)

class User_Details(models.Model):
    # User Details
    User = models.OneToOneField(User, on_delete=models.CASCADE, db_column="User", to_field="username",unique=True)
    Profile = models.ImageField(default=default_static_image_path, null=True, blank=True, upload_to=user_profile_path)
    Gender = models.CharField(max_length=10,default='Male')
    Contact = models.CharField(max_length=50, default='+233')
    City=models.CharField(max_length=100,default='Kumasi')
    Town=models.CharField(max_length=100,default='Santasi')
    # Education And Qualification
    Address=models.TextField(default='Geo location')
    About = models.TextField(default="Hi there, i am a doctor at Framada <(*v*)>")
    Level=models.CharField(max_length=50)

    def __str__(self):
        return ('%s %s'%(self.User.first_name,self.User.last_name))

    class Meta:
        db_table = "user_details"
        verbose_name='User Detail'

    def save(self, *args, **kwargs):
        self.Profile=compress_images(self.Profile)
        super(User_Details, self).save(*args, **kwargs)

@receiver(pre_save, sender=User_Details)
def pre_save_image(sender, instance, *args, **kwargs):
    # print('moddel presave excuted')
    """ instance old image file will delete from os """
    try:
        old_img = instance.__class__.objects.get(id=instance.id).Profile.path
        try:
            new_img = instance.Profile.path
        except:
            new_img = None
        if new_img != old_img:
            if os.path.exists(old_img):
                os.remove(old_img)
    except:
        pass

@receiver(post_delete, sender=User_Details)
def post_save_image(sender, instance, *args, **kwargs):
    """ Clean Old Image file """
    try:
        instance.Profile.delete(save=False)
    except:
        pass

class Insurance(models.Model):
    Name = models.CharField(max_length=50,unique=True)
     
    def __str__(self):
        return self.Name

    def save(self, *args, **kwargs):
        self.Name = str(self.Name).upper()
        super(Insurance, self).save(*args, **kwargs)

    class Meta:
        db_table = "insurance"

class Modalities(models.Model):
    Modality = models.CharField(max_length=50,unique=True)
    Acronym = models.CharField(max_length=10)
     
    def __str__(self):
        return '%s-%s'%(self.Modality,self.Acronym)

    class Meta:
        db_table = "modalities"
        verbose_name='modalitie'

class Procedures(models.Model):
    Procedure = models.CharField(max_length=100)
    Charge = models.DecimalField(max_digits=50,decimal_places=2)
    Modality=models.ForeignKey(Modalities,on_delete=models.CASCADE,db_column='Modality')
    Tag = models.CharField(max_length=50,choices=(('Radiology','Radiology'),('Laboratory','Laboratory')))
    
    def __str__(self):
        return f'{self.Procedure}-{self.Modality.Acronym}'

    class Meta:
        db_table = "procedures"
        verbose_name='Procedure'

class Referring_Facilities(models.Model):
    Facility_Name = models.CharField(max_length=100,unique=True)
   
    def __str__(self):
        return self.Facility_Name

    def save(self, *args, **kwargs):
        self.Facility_Name = str(self.Facility_Name).title()
        super(Referring_Facilities, self).save(*args, **kwargs)

    class Meta:
        db_table = "referring_facilities"
        verbose_name='Referring Facilitie'

class Consulting_Room(models.Model):
    Room_Name = models.CharField(max_length=50,unique=True)
    Description = models.TextField()
     
    def __str__(self):
        return '%s'%(self.Room_Name)

    def save(self, *args, **kwargs):
        self.Room_Name = str(self.Room_Name).title()
        super(Consulting_Room, self).save(*args, **kwargs)

    class Meta:
        db_table = "consulting_room"

class Patients_Checker(models.Model):
    Patient_Id = models.CharField(max_length=20, primary_key=True, unique=True)
    Reg_Date = models.DateField(auto_now=True)

    class Meta:
        db_table = "patients_checker"

    def __str__(self):
        return '{0}-{1}'.format(self.Patient_Id,self.Reg_Date)

class Patients(models.Model):
    Patient_Id= models.CharField(max_length=50,unique=True)
    Profile = models.ImageField(default=default_static_image_path, null=True, blank=True, upload_to=patients_profile_path)
    First_Name = models.CharField(max_length=50)
    Surname = models.CharField(max_length=50)
    DOB = models.DateField(auto_now=False,default=timezone.now)
    Age= models.CharField(max_length=10)
    Gender = models.CharField(max_length=10)
    Residence=models.CharField(max_length=50)
    Nationality=models.CharField(max_length=50)
    Tel=models.CharField(max_length=15)
    Emergency_Tel=models.CharField(max_length=15,null=True)
    Occupation=models.CharField(max_length=100,default='None')
    Email=models.EmailField(default='someone@here.com')
    Date_Joined=models.DateField(auto_now=False)
    Last_Visit=models.DateTimeField(auto_now=False)
    Insurance_Type=models.ForeignKey(Insurance,on_delete=models.CASCADE,db_column='Insurance_Type',null=True)
    Insurance_Id=models.CharField(max_length=50,default='xxx-xxxx-xxx')
    Balance=models.DecimalField(max_digits=50,decimal_places=2,default=0)
    Status=models.CharField(max_length=20,default='Waiting')
    Time=models.TimeField(auto_now=True)
     
    def __str__(self):
        return '%s %s'%(self.First_Name,self.Surname)

    class Meta:
        db_table = "patients"
    
    def save(self, *args, **kwargs):
        self.First_Name = str(self.First_Name).title()
        self.Surname = str(self.Surname).title()
        self.Residence = str(self.Residence).title()
        self.Occupation = str(self.Occupation).title()
        self.Profile=compress_images(self.Profile)
        super(Patients, self).save(*args, **kwargs)

class Treatment_Alert(models.Model):
    Message = models.TextField()
    Treatments = models.TextField()
    Send_Alert = models.TextField(max_length=50)
    
    def __str__(self):
        return f'{self.Treatments}-{self.Message}'

    class Meta:
        db_table = "treatment_alert"

class Birthday_Wishes(models.Model):
    Patient_Id= models.ForeignKey(Patients,on_delete=models.CASCADE,db_column='Patient_Id')
    Message=models.TextField()
    New_Age=models.IntegerField()
    Delivery_Status=models.BooleanField(default=False)
    Due_Date=models.DateField(auto_now=True)
     
    def __str__(self):
        return '%s %s'%(self.Patient_Id.First_Name,self.Patient_Id.Surname)

    class Meta:
        db_table = "birthday_wishes"
    
@receiver(pre_save, sender=Patients)
def pre_save_image(sender, instance, *args, **kwargs):
    # print('moddel presave excuted')
    """ instance old image file will delete from os """
    try:
        old_img = instance.__class__.objects.get(id=instance.id).Profile.path
        try:
            new_img = instance.Profile.path
        except:
            new_img = None
        if new_img != old_img:
            if os.path.exists(old_img):
                os.remove(old_img)
    except:
        pass

@receiver(post_delete, sender=Patients)
def post_save_image(sender, instance, *args, **kwargs):
    """ Clean Old Image file """
    try:
        instance.Profile.delete(save=False)
    except:
        pass

class Vitals(models.Model):
    Patient_Id= models.ForeignKey(Patients,on_delete=models.CASCADE,db_column='Patient_Id')
    Procedure = models.ForeignKey(Procedures,on_delete=models.CASCADE,db_column='Procedure')
    Department=models.CharField(max_length=50,default='Bill Payment') #This field is use to check where patient is
    Status=models.CharField(max_length=50,default='Waiting')
    Referring_Facility=models.CharField(max_length=100,null=True,default='None')
    Referred_Doctor=models.CharField(max_length=50,null=True,default='None')
    # payment side
    Treatment_Amount = models.DecimalField(max_digits=50,decimal_places=2)
    Paid_Amount = models.DecimalField(max_digits=50,decimal_places=2,default=0)
    Trans_Id=models.CharField(max_length=250)
    # 
    Logger=models.CharField(max_length=50)
    Date=models.DateField(auto_now=True)
    Time=models.TimeField(auto_now=True)

    def __str__(self):
        return '%s(%s)'%(self.Patient_Id,self.Complaints)

    class Meta:
        db_table = "vitals"

# Patients Complaints By Doctors
class Presenting_Complaints(models.Model):
    # categories=(('Medical History','Medical History'),('Clinical Note','Clinical Note'),('Systemic Enquiries','Systemic Enquiries'))
    Patient_Id= models.ForeignKey(Patients,on_delete=models.CASCADE,db_column='Patient_Id')
    Complaint_Category=models.CharField(max_length=50)
    Complaint_Type=models.CharField(max_length=50)
    Complaints = models.TextField(default='None')
    Docs_Complaints = models.TextField(default='None')
    # lab technician
    Tech_Instance=models.ForeignKey(User_Details,on_delete=models.SET_NULL,null=True,db_column='Tech_Instance',related_name="Tech_Instance_Logger")
    Tech_Report = models.FileField(upload_to=patients_docs_path,default=default_static_image_path,null=True,blank=True)
    Tech_Report_Name=models.CharField(max_length=50,default='None')
    # doc statement of report
    Docs_Instance=models.ForeignKey(User_Details,on_delete=models.SET_NULL,null=True,db_column='Docs_Instance',related_name="Docs_Instance_Logger")
    Docs_Report = models.FileField(upload_to=patients_docs_path,default=default_static_image_path,null=True,blank=True)
    Docs_Report_Name=models.CharField(max_length=50,default='None')
    Vitals=models.ForeignKey(Vitals,on_delete=models.SET_NULL,null=True,db_column='Vitals')
    Date=models.DateField(auto_now=True)
    Time=models.TimeField(auto_now=True)

    def __str__(self):
        return ('%s-(%s)-%s'%(self.Patient_Id,self.Complaints,self.Complaint_Type))

    class Meta:
        db_table = "presenting_complaints"

    def save(self, *args,**kwargs):
        return super(Presenting_Complaints,self).save(*args,**kwargs)

# Payment_Journal 
class Payment_Journal(models.Model):
    Patient_Id= models.ForeignKey(Patients,on_delete=models.CASCADE,db_column='Patient_Id')
    Treatment_Name = models.TextField()
    Treatment_Amount = models.DecimalField(max_digits=50,decimal_places=2)
    Paid_Amount = models.DecimalField(max_digits=50,decimal_places=2,default=0)
    Note = models.TextField(default='Not Specified')
    Logger_Instance=models.ForeignKey(User_Details,on_delete=models.SET_NULL,null=True,db_column='Logger_Instance')
    Date=models.DateField(auto_now=True)
    Time=models.TimeField(auto_now=True)

    def __str__(self):
        return ('%s(%s)-%s'%(self.Patient_Id,self.Treatment_Name,self.Treatment_Amount))

    class Meta:
        db_table = "payment_journal"
    
    def save(self, *args, **kwargs):
        # self.Treatment_Name = str(self.Treatment_Name).title()
        # just update patient balance with charge(Treatment_Amount) as negative on every new insert/save of the patient
        Patients.objects.filter(Patient_Id=self.Patient_Id.Patient_Id).update(Balance=F('Balance')-self.Treatment_Amount)
        super(Payment_Journal, self).save(*args, **kwargs)

# Payment Journal History 
class Journal_History(models.Model):
    Payment_Journal = models.ForeignKey(Vitals,on_delete=models.CASCADE,db_column='Payment_Journal')
    Paid_Amount = models.DecimalField(max_digits=50,decimal_places=2,default=0)
    Payment_Type=models.CharField(max_length=20)
    Approved_By=models.CharField(max_length=50)
    Payment_Comment=models.TextField(null=True)
    Date=models.DateField(auto_now=False)
    Time=models.TimeField(auto_now=True)

    def __str__(self):
        return ('%s(%s)-%s'%(self.Payment_Journal.Patient_Id,self.Payment_Journal.Treatment_Amount,self.Paid_Amount))

    class Meta:
        db_table = "journal_history"

# Journal History Checker
class Journal_History_Checker(models.Model):
    Trans_Id = models.CharField(max_length=250, primary_key=True, unique=True)
    Cashier = models.CharField(max_length=50)
    Date = models.DateField(auto_now=True)

    class Meta:
        db_table = "journal_history_checker"

    def __str__(self):
        return '{0}-{1}'.format(self.Cashier,self.Trans_Id)

# Requisition Approval_Authority
class Approval_Authority(models.Model):
    Limited_Amount = models.DecimalField(max_digits=50,decimal_places=2,unique=True)
    Authorizer=models.OneToOneField(User_Details, on_delete=models.CASCADE, db_column="Authorizer")
    Date=models.DateField(auto_now=True)
    Time=models.TimeField(auto_now=True)

    def __str__(self):
        return f'{self.Authorizer}-({self.Limited_Amount})'

    class Meta:
        db_table = "approval_authority"
        verbose_name='Requisition Authorizer'

# Requisition
class Requisition(models.Model):
    Placeholder=models.ForeignKey(User_Details,on_delete=models.CASCADE, db_column="Placeholer")
    Description=models.TextField()
    Delivery_Timeline=models.CharField(max_length=50)
    Quantity = models.IntegerField()
    Price = models.DecimalField(max_digits=50,decimal_places=2,default=0)
    Total_Cost = models.DecimalField(max_digits=50,decimal_places=2,default=0)
    Approval_Authority=models.ManyToManyField(Approval_Authority, db_column="Approval_Authority")
    Approval_Status=models.CharField(max_length=50,default='Pending')
    Delivery_Status=models.CharField(max_length=50,default='Pending')
    Approved_By=models.CharField(max_length=50,default='Pending')
    Date=models.DateField(auto_now=True)
    Time=models.TimeField(auto_now=True)

    class Meta:
        db_table = "requisition"
        verbose_name='Requisition'

# Web Models
class Appoitment(models.Model):
    Name=models.CharField(max_length=50)
    Phone=models.CharField(max_length=50)
    Email=models.CharField(max_length=50)
    Preferred_Date=models.DateField(auto_now=False)
    Message = models.TextField()
    Preferred_Time=models.CharField(max_length=20)
    Date=models.DateField(auto_now=True)
    Time=models.TimeField(auto_now=True)

    def __str__(self):
        return ('%s(%s)'%(self.Name,self.Message))

    class Meta:
        db_table = "appointment"
    
    def save(self, *args, **kwargs):
        self.Name = str(self.Name).title()
        self.Message=str(self.Message).replace('\r\n','\\n')
        self.Message=str(self.Message).replace('\n','\\n')
        super(Appoitment, self).save(*args, **kwargs)

class Message(models.Model):
    Name=models.CharField(max_length=50)
    Phone=models.CharField(max_length=50)
    Email=models.CharField(max_length=50)
    Message = models.TextField()
    Date=models.DateField(auto_now=True)
    Time=models.TimeField(auto_now=True)

    def __str__(self):
        return ('%s(%s)'%(self.Name,self.Message))

    class Meta:
        db_table = "message"
    
    def save(self, *args, **kwargs):
        self.Name = str(self.Name).title()
        self.Message=str(self.Message).replace('\r\n','\\n')
        self.Message=str(self.Message).replace('\n','\\n')
        super(Message, self).save(*args, **kwargs)

# PHARMACY MODELS
class Stocks_Department(models.Model):
    Name=models.CharField(max_length=50,unique=True,default=None)
    Date=models.DateField(auto_now=True)

    def __str__(self):
        return self.Name

    class Meta:
        db_table="pos_stocks_department"
    
    def save(self, *args, **kwargs):
        self.Name=str(self.Name).upper()
        super(Stocks_Department, self).save(*args, **kwargs)

class Supplier(models.Model):
    Company_Name = models.CharField(max_length=50,unique=True)
    Contact = models.CharField(max_length=50)
    Address = models.TextField()
    Date=models.DateField(auto_now=True)
    def __str__(self):
        return self.Company_Name
        
    class Meta:
        db_table = "pos_supplier"

    def save(self, *args,**kwargs):
        self.Company_Name=str(self.Company_Name).upper()
        self.Address=str(self.Address).title()
        return super().save(*args, **kwargs)

class Stocks(models.Model):
    Product_Id = models.CharField(max_length=50, primary_key=True,unique=True)
    Product_Name = models.CharField(max_length=50)
    Department = models.ForeignKey(Stocks_Department,on_delete=models.CASCADE,db_column='Department')
    Quantity = models.IntegerField()
    Vat = models.DecimalField(decimal_places=2, max_digits=50, null=True, default=0.00)
    Retail = models.DecimalField(decimal_places=2, max_digits=50)
    Whole_Sale = models.DecimalField(decimal_places=2, max_digits=50)
    Purchase = models.DecimalField(decimal_places=2, max_digits=50)
    Total = models.DecimalField(decimal_places=2, max_digits=50)
    Rprofit = models.DecimalField(decimal_places=2, max_digits=50, null=True, default=0.00)
    Wprofit = models.DecimalField(decimal_places=2, max_digits=50, null=True, default=0.00)
    Expiry_Date=models.DateField(auto_now=False)
    # supplier details
    Suppliers = models.ForeignKey(Supplier, on_delete=models.CASCADE,db_column="Suppliers")
    Invoice = models.CharField(max_length=50, default=None)
    
    class Meta:
        db_table = "pos_stocks"

    def save(self, *args, **kwargs):
        self.Product_Name=str(self.Product_Name).upper()
        super(Stocks, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.Product_Name

class Stocks_Checker(models.Model):
    Product_Id = models.CharField(max_length=50)
    Product_Name=models.CharField(max_length=50)
    
    class Meta:
        db_table = "pos_stocks_checker"

    def __str__(self) -> str:
        return "%s(%s)" %(self.Product_Name,self.Product_Id)

class New_Stocks(models.Model):
    Product_Id = models.CharField(max_length=50)
    Product_Name = models.CharField(max_length=50)
    Department = models.ForeignKey(Stocks_Department,on_delete=models.CASCADE,db_column='Department')
    Quantity = models.IntegerField()
    Vat = models.DecimalField(decimal_places=2, max_digits=50, null=True, default=0.00)
    Retail = models.DecimalField(decimal_places=2, max_digits=50)
    Whole_Sale = models.DecimalField(decimal_places=2, max_digits=50)
    Purchase = models.DecimalField(decimal_places=2, max_digits=50)
    Total = models.DecimalField(decimal_places=2, max_digits=50)
    Rprofit = models.DecimalField(decimal_places=2, max_digits=50, null=True, default=0.00)
    Wprofit = models.DecimalField(decimal_places=2, max_digits=50, null=True, default=0.00)
    # supplier details
    Suppliers = models.ForeignKey(Supplier, on_delete=models.CASCADE,db_column="Suppliers")
    Invoice = models.CharField(max_length=50, default=None)
    Date = models.DateField(auto_now=True)
     
    class Meta:
        db_table = "pos_new_stocks"

    def save(self, *args, **kwargs):
            self.Product_Name=str(self.Product_Name).upper()
            super(New_Stocks, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.Product_Name

# Patient Prescriptions
class Drugs_Prescriptions(models.Model):
    Patient_Id= models.ForeignKey(Patients,on_delete=models.CASCADE,db_column='Patient_Id')
    Drug_Id=models.ForeignKey(Stocks,on_delete=models.CASCADE,db_column='Drug_Id')
    Quantity=models.IntegerField()
    Price=models.DecimalField(decimal_places=2,max_digits=50)
    Cost=models.DecimalField(decimal_places=2,max_digits=50)
    Amount_Paid=models.DecimalField(decimal_places=2,max_digits=50,default=0)
    Frequency = models.CharField(max_length=50) 
    Others = models.CharField(max_length=10,default='Not Specified')
    Duration=models.TextField(default='Not Specified')
    Start_Date=models.DateField(auto_now=False)
    End_Date=models.DateField(auto_now=False)
    Logger_Instance=models.ForeignKey(User_Details,on_delete=models.CASCADE,db_column='Logger_Instance')
    Journal_Id= models.ForeignKey(Payment_Journal,on_delete=models.CASCADE,db_column='Journal_Id')
    Sales_Status=models.CharField(max_length=20,default='Pending')
    Date=models.DateField(auto_now=True)
    Time=models.TimeField(auto_now=True)

    def __str__(self):
        return '%s-(%s-%s)'%(self.Patient_Id,self.Drug_Id,self.Quantity)

    class Meta:
        db_table = "drugs_prescriptions"

class Sale(models.Model):
    product = models.CharField(max_length=50)
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)