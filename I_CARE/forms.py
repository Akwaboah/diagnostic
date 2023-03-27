from I_CARE.models import Insurance, Patients,User_Details,Stocks
from django import forms
from django.contrib.auth.models import Group
from I_CARE.utils import countries as country_tuple, user_levels,DATE_INPUT_FORMATS


class Patients_Form(forms.ModelForm):
    # tab1 Fields
    Profile = forms.ImageField(label='', required=False,widget=forms.FileInput(attrs={'class': 'upload','onchange':'checkImage(event);','data-tab': 'tab1'}))
    First_Name=forms.CharField(required=True,widget=forms.TextInput(attrs={'autocomplete':'off','placeholder':'First Name','autocapitalize':'sentences','data-tab': 'tab1'}))
    Surname=forms.CharField(required=True,widget=forms.TextInput(attrs={'autocomplete':'off','placeholder':'Surname','data-tab': 'tab1'}))
    DOB=forms.DateField(input_formats=DATE_INPUT_FORMATS,required=True,widget=forms.DateInput(attrs={'placeholder':'Date Of Birth','autocomplete':'off','onkeyup':'CalcAge(this.value);','data-tab': 'tab1'}))
    Age=forms.CharField(required=False,widget=forms.TextInput(attrs={'autocomplete':'off','placeholder':'Age','data-tab': 'tab1'}))
    Residence=forms.CharField(required=True,widget=forms.TextInput(attrs={'autocomplete':'off','placeholder':'Residence','data-tab': 'tab1'}))
    Nationality= forms.ChoiceField(required=True,choices=country_tuple,widget=forms.Select(attrs={'class': 'form-control form-control-sm','data-tab': 'tab1'}))
    Tel=forms.CharField(required=True,widget=forms.TextInput(attrs={'autocomplete':'off','placeholder':'Telephone','data-tab': 'tab1'}))
    Emergency_Tel=forms.CharField(required=False,widget=forms.TextInput(attrs={'autocomplete':'off','placeholder':'Emergency Contact','data-tab': 'tab1'}))
    # tab2 Fields
    Occupation=forms.CharField(required=False,widget=forms.TextInput(attrs={'autocomplete': 'off','placeholder':'Occupation','data-tab': 'tab2'}))
    Email=forms.CharField(required=False,widget=forms.EmailInput(attrs={'autocomplete': 'off','placeholder':'Email Address','data-tab': 'tab2'}))
    Reffered_Doctor=forms.CharField(required=False,widget=forms.TextInput(attrs={'autocomplete': 'off','placeholder':'Referring Doctor','data-tab': 'tab2'}))
    Insurance_Type = forms.ModelChoiceField(queryset=Insurance.objects.all(), required=False,widget=forms.Select(attrs={'data-tab': 'tab2'}))
    Insurance_Id=forms.CharField(required=False,widget=forms.TextInput(attrs={'autocomplete': 'off','placeholder':'Insurance ID','data-tab': 'tab2'}))
     
    class Meta:
        model = Patients
        fields = '__all__'
        exclude = {'Patient_Id','Gender','Date_Joined','Last_Visit','Department','Status','Balance','Procedure'}
   
    def __init__(self, *args, **kwargs):
        super(Patients_Form, self).__init__(*args, **kwargs)
        for name in self.fields.keys():
            if name !='Profile':
                self.fields[name].widget.attrs.update({
                    'class': 'form-control',
                })
        self.fields['Nationality'].initial='Ghanaian'
        self.fields['Insurance_Type'].empty_label='Select Insurance'

class Staff_Form(forms.ModelForm):
  
    Profile = forms.ImageField(label='', required=False,widget=forms.FileInput(attrs={'class': 'upload','onchange':'checkImage(event);'}))
    Contact=forms.CharField(required=True,widget=forms.TextInput(attrs={'autocomplete': 'off','class': 'form-control'}))
    City =forms.CharField(required=False,widget=forms.TextInput(attrs={'autocomplete': 'off','class': 'form-control'}))
    Town =forms.CharField(required=False,widget=forms.TextInput(attrs={'autocomplete': 'off','class': 'form-control'}))
    Address=forms.CharField(required=True,widget=forms.TextInput(attrs={'autocomplete': 'off','class': 'form-control'}))
    About=forms.CharField(required=False,widget=forms.Textarea(attrs={'autocomplete': 'off','style':'height: 5em','class': 'form-control'}))

    class Meta:
        model = User_Details
        fields = '__all__'
        exclude = {'Gender','User','Level'}
   
    def __init__(self, *args, **kwargs):
        super(Staff_Form, self).__init__(*args, **kwargs)
         
# Pharmacy 
class Stocks_Form(forms.ModelForm):
    Product_Id=forms.CharField(required=False,widget=forms.TextInput(attrs={"autocomplete": "off","placeholder":"Product Id","readonly":"true",}))
    Product_Name=forms.CharField(required=True,widget=forms.TextInput(attrs={"autocomplete": "off","placeholder":"Product Name *"}))
    Expiry_Date=forms.DateField(input_formats=['%Y-%m'],required=True,widget=forms.TextInput(attrs={"autocomplete": "off","placeholder":"yyyy-mm *"}))
    Quantity=forms.CharField(required=True,widget=forms.NumberInput(attrs={"autocomplete": "off","onkeyup": "Quantity_Cal();","onchange": "Quantity_Cal();","type":"number"}))
    Purchase=forms.CharField(required=True,widget=forms.NumberInput(attrs={"autocomplete": "off","onkeyup": "Quantity_Cal();","onchange": "Quantity_Cal();","type":"number","step":"any"}))
    Invoice=forms.CharField(required=False,widget=forms.TextInput(attrs={"placeholder":"Invoice Number"}))
    Total=forms.CharField(required=True,widget=forms.NumberInput(attrs={"readonly":"true","type":"number","step":"any"}))
    Retail=forms.CharField(required=True,widget=forms.NumberInput(attrs={"type":"number","step":"any"}))
    Whole_Sale=forms.CharField(required=True,widget=forms.NumberInput(attrs={"type":"number","step":"any"}))
    Vat=forms.CharField(required=False,widget=forms.NumberInput(attrs={"readonly":"true","id": "vat_value_id",'value':'0.00'}))
   
    class Meta:
        model = Stocks
        fields = ['Product_Id','Product_Name','Quantity','Vat','Retail','Suppliers',
                'Whole_Sale' ,'Purchase','Total','Invoice','Department','Expiry_Date']

    def __init__(self, *args, **kwargs):
        super(Stocks_Form, self).__init__(*args, **kwargs)
        self.fields["Department"].empty_label = "Department Type*" 
        self.fields["Suppliers"].empty_label = "Supplier"
        
        for name in self.fields.keys():
            if name in ['Department','Suppliers']:
                self.fields[name].widget.attrs.update({
                    'class': 'form-control',
                })
            else:
                self.fields[name].widget.attrs.update({
                    'class': 'form-control text-center',
                })






