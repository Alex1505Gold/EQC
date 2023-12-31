from django.shortcuts import render, redirect
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect, ensure_csrf_cookie
from .utils import is_ajax, classify_face
import base64
from logs.models import Log
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from qsystem.models import Profile
from collections import deque
from datetime import datetime

visitors = deque()

@ensure_csrf_cookie
def login_student_view(request):
    return render(request, 'login_student.html', {})

def logout_view(request):
    logout(request)
    return redirect('home')

def home_view(request):
    visitors_req = list(visitors)
    return render(request, 'main.html', {'visitors' : visitors_req})

def prof_view(request):
    visitors_req = list(visitors)
    if len(visitors_req) > 0:
        print(visitors_req[0].photo.path)
        photo_path_ind = (str(visitors_req[0].photo.path)).find('media')
        if photo_path_ind > -1:
            photo_path = (str(visitors_req[0].photo.path))[photo_path_ind:]
            print(photo_path)
            return render(request, 'main_professor.html', {'visitors' : visitors_req, 'photo_path' : photo_path})
    return render(request, 'main_professor.html', {'visitors' : visitors_req, 'photo_path' : ''})


@login_required
def student_view(request):
    visitors_req = list(visitors)
    return render(request, 'main_student.html', {'visitors' : visitors_req})

def find_user_view(request):
    if is_ajax(request):
        photo = request.POST.get('photo')
        _, str_img = photo.split(';base64')

        # print(photo)
        decoded_file = base64.b64decode(str_img)
        # print(decoded_file)

        x = Log()
        x.photo.save('upload.png', ContentFile(decoded_file))
        x.save()

        res = classify_face(x.photo.path)
        if res:
            user_exists = User.objects.filter(username=res).exists()
            if user_exists:
                user = User.objects.get(username=res)
                profile = Profile.objects.get(user=user)
                x.profile = profile
                x.save()
                if profile not in visitors:
                    visitors.append(profile)
                for v in visitors:
                    print(v.user.first_name, v.user.last_name)
                login(request, user)
                return JsonResponse({'success': True})
        return JsonResponse({'success': False})
    
def delete_visitor_view(request):
    if len(visitors) > 0:
        profile = visitors.popleft()
    return redirect('prof')