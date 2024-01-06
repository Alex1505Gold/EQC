"""
URL configuration for EQC_asvt project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    login_student_view,
    logout_view,
    home_view,
    find_user_view,
    student_view,
    delete_visitor_view,
    prof_view,
    sign_up_view,
    create_user_view,
    verify_view,
    mail_note_view,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('login_student/', login_student_view, name='login-student'),
    path('logout/', logout_view, name='logout'),
    path('classify/', find_user_view, name='classify'),
    path('student/', student_view, name='student'),
    path('del_visitor/', delete_visitor_view, name='del-visitor'),
    path('prof/', prof_view, name='prof'),
    path('sign_up/', sign_up_view, name='sign-up'),
    path('create/', create_user_view, name='create'),
    path('verify/<auth_token>' , verify_view ,name = "verify"),
    path('notification/' , mail_note_view ,name = "notification"),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
