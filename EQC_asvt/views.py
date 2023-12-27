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

visitors = deque()

@ensure_csrf_cookie
def login_view(request):
    return render(request, 'login.html', {})

def logout_view(request):
    logout(request)
    return redirect('login')

#@login_required
def home_view(request):
    visitors_req = list(visitors)
    return render(request, 'main.html', {'visitors' : visitors_req})

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
    
def delete_visitor(request):
    profile = visitors.popleft()
    return JsonResponse({'profile' : str(profile)})