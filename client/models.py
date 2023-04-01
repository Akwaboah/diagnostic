from django.db import models
from django_tenants.models import TenantMixin, DomainMixin
# Create your models here.
class Client(TenantMixin):
    name = models.CharField(max_length=100)

class Domain(DomainMixin):
    pass