import os
from django.db.models.signals import pre_save,post_delete,post_save,\
    m2m_changed
from django.dispatch import receiver
from django.urls import reverse
from django.db.models import F
from I_CARE.models import Patients, Societies, User_Details, Vitals,\
    Vitals_Discount
from I_CARE.views import CUS_MAIL

# Patients Signals
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
def post_del_image(sender, instance, *args, **kwargs):
    """ Clean Old Image file """
    try:
        instance.Profile.delete(save=False)
    except:
        pass

@receiver(post_save, sender=Patients)
def patient_post_save(sender, instance, *args, **kwargs):
    """ save default society for patients """
    if not instance.Societies.exists():
        default_society, _ = Societies.objects.get_or_create(Name='No Society')
        instance.Societies.add(default_society)

# Vitals Signals
@receiver(post_delete, sender=Vitals)
def post_del_vitals(sender, instance, *args, **kwargs):
    """ Revert the charge from the patient account balance"""
    Patients.objects.filter(Patient_Id=instance.Patient_Id.Patient_Id).update(Balance=F('Balance')+instance.Treatment_Amount)

@receiver(m2m_changed, sender=Vitals_Discount.Procedure.through)
def on_discounted_vitals(sender, instance, action, pk_set, **kwargs):
    """ Forward email to the authorizers to haandle the approvals"""
    if action == 'post_add':

        subject = 'Request for approval of discount'
        
        message = """
        Dear Authorizers,

        I am writing to request your approval for a discount that I granted to a client during today's transaction.
    
        Here are the details of the transaction:

        - Client Name: {client_name}
        - Date: {date}
        - Procedures(s): {procedures}
        - Total Amount: {total_amount}
        - Discount Amount: {discount_amount}

        The reason given for the discount was {reason}. 

        Please click on the link to approve or reject this request: {discount_url}

        I would appreciate your prompt review of this request. Please let me know if you have any questions or concerns.

        Thank you for your attention to this matter.

        Best regards,
        {your_name}
        """

        procedure_values = instance.Procedure.all().values_list('Procedure', flat=True)
        # Join the list of values into a comma-separated string
        procedure_string = ', '.join(procedure_values)
        msgBody = message.format(
            client_name=instance.Patient_Id,
            date=instance.Date,
            procedures=procedure_string,
            total_amount=instance.Total_Cost,
            discount_amount=instance.Discount,
            reason=instance.Reason,
            your_name=instance.Logger,
            discount_url='https://www.routhealth.com/requisition/discount-approval',
        )
        to_email=[]
        res=CUS_MAIL(subject,msgBody,to_email).sendMail('Auth')

# User_Details signals
@receiver(pre_save, sender=User_Details)
def remove_saved_image(sender, instance, *args, **kwargs):
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
def post_del_image(sender, instance, *args, **kwargs):
    """ Clean Old Image file """
    try:
        instance.Profile.delete(save=False)
    except:
        pass


