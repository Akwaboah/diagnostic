from I_CARE.models import User_Details
from django.contrib.auth.models import User
from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver


@receiver(post_save,sender=User_Details)
def my_callback(sender, **kwargs):
    print("Request finished!, user details object updated")

