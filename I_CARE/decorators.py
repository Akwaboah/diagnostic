from django.http import HttpResponse
from django.shortcuts import redirect
from datetime import datetime
# Django password hashing and validating imports 
from django.contrib.auth.hashers import check_password
 
def unauthenticated_staffs(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_anonymous==False:
            # if validate_subscription():
                # allow authenticated users, un-anonymous-user and registered system to perform their actions and return their views
                return view_func(request, *args, **kwargs)
            # else:
            #     return redirect("/height/activate-system")
        else:
            # if not authenticated or is anonymous then redirect to login page
            return redirect('/staff/login')
    return wrapper_func

def unauthenticated_patients(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_anonymous==False:
            # if validate_subscription():
                # allow authenticated users, un-anonymous-user and registered system to perform their actions and return their views
                return view_func(request, *args, **kwargs)
            # else:
            #     return redirect("/height/activate-system")
        else:
            # if not authenticated or is anonymous then redirect to login page
            return redirect('/staff/login')
    return wrapper_func
 
def class_allow_users(allowed_levels=[]):
    def decorator(view_func):
        def wrapper_fun(request, *args, **kwargs):
            if request.user.groups.exists():
                # doctors
                if request.user.groups.filter(name__in=allowed_levels):
                    return view_func(request, *args, **kwargs)
                # opd
                elif request.user.groups.filter(name__in=['Security']):
                    return redirect('/info/no-response')
                else:
                    return redirect('/opd/dashboard')
            else:
                return HttpResponse('No User Account Level Specified')
        return wrapper_fun
    return decorator
