from django.urls import path
import I_CARE.views as views

urlpatterns = [
     path(route='',view=views.Home_Page.as_view(),name='home-page'),
     path(route='info/<str:page>',view=views.Home_Page_Links.as_view(),name='web-links'),
     path(route='staff/<str:page>',view=views.Auth_Staffs.as_view(),name='auth-staff'),
     path(route='opd/<str:page>',view=views.OPD.as_view(),name='opd'),
     path(route='nursing/<str:page>',view=views.Payment_Department.as_view(),name='nursing'),
     path(route='lab/<str:page>',view=views.Laboratory.as_view(),name='lab'),
     path(route='radiology/<str:page>',view=views.Imaging.as_view(),name='radiology'),
     path(route='doc/<str:page>',view=views.Doctors.as_view(),name='doc'),
     path(route='pharm/<str:page>',view=views.Pharmacy.as_view(),name='pharm'),
     path(route='reporting/<str:page>/<str:type>',view=views.General_Reports.as_view(),name='reporting'),
     path(route='requisition/<str:page>',view=views.Requisition_Form.as_view(),name='requisition'),
     path('alerts/<str:page>',views.CUS_SMS.as_view(),name='alerts'),
]
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
