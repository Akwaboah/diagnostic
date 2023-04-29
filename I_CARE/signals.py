import os
from django.db.models.signals import pre_save,post_delete,post_save
from django.dispatch import receiver
from django.db.models import F
from I_CARE.models import Patients, Societies, User_Details, Vitals

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
def post_save(sender, instance, *args, **kwargs):
    """ save default society for patients """
    if not instance.Societies.exists():
        default_society, _ = Societies.objects.get_or_create(Name='No Society')
        instance.Societies.add(default_society)

# Vitals Signals
@receiver(post_delete, sender=Vitals)
def post_del_vitals(sender, instance, *args, **kwargs):
    """ Revert the charge from the patient account balance"""
    Patients.objects.filter(Patient_Id=instance.Patient_Id.Patient_Id).update(Balance=F('Balance')+instance.Treatment_Amount)
   
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
