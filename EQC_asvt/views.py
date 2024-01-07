from django.shortcuts import render, redirect
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect, ensure_csrf_cookie
from .utils import is_ajax, classify_face, bio_to_username
import base64
from logs.models import Log
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from qsystem.models import Profile
from collections import deque
from datetime import datetime
from .settings import EMAIL_HOST_USER
from django.core.mail import send_mail

visitors = deque()
curVisitor = None
counter = 0

allowed_mails_list = [
    "sgolenkov2002@gmail.com",
]

allowed_mails = set(allowed_mails_list)

@ensure_csrf_cookie
def sign_up_view(request):
    return render(request, 'sign_up.html', {})

@ensure_csrf_cookie
def login_student_view(request):
    return render(request, 'login_student.html', {})

@ensure_csrf_cookie
def login_password_view(request):
    return render(request, 'login_password.html', {})

def logout_view(request):
    logout(request)
    return redirect('home')

def home_view(request):
    visitors_req = list(visitors)
    return render(request, 'main.html', {'visitors' : visitors_req, 'curVisitor' : curVisitor})

@login_required
def prof_view(request):
    curUser = request.user
    curProfile = Profile.objects.filter(user = curUser).first()
    if curProfile.acc_type != 'professor':
        return redirect('login-password')
    visitors_req = list(visitors)
    students = Profile.objects.filter(acc_type='Student').all()
    photo_path = ''
    if curVisitor is not None:
        print(curVisitor.photo.path)
        photo_path_ind = (str(curVisitor.photo.path)).find('media')
        if photo_path_ind > -1:
            photo_path = (str(curVisitor.photo.path))[photo_path_ind:]
            print(photo_path)
    highlighted = students[globals()['counter']]
    photo_path_ind = (str(highlighted.photo.path)).find('media')
    if photo_path_ind > -1:
        photo_highlited_path = (str(highlighted.photo.path))[photo_path_ind:]
    return render(request, 'main_professor.html', {'visitors' : visitors_req, 'photo_path' : photo_path,
                                                   'students' : students, 'curVisitor' : curVisitor,
                                                   'highlighted' : highlighted, 'photo_highlighted_path' : photo_highlited_path})


@login_required
def student_view(request):
    visitors_req = list(visitors)
    return render(request, 'main_student.html', {'visitors' : visitors_req, 'curVisitor' : curVisitor})

def password_auth_view(request):
    if is_ajax(request):
        username = request.POST.get('user')
        password = request.POST.get('password')
        curUser = authenticate(username=username, password=password)
        if curUser is None:
            return JsonResponse({'success' : False, 'info' : 'Username or password is incorrect'})
        curProf = Profile.objects.filter(user=curUser).first()
        if curProf.acc_type != 'professor':
            return JsonResponse({'success' : False, 'info' : 'You are not a professor'})
        login(request, curUser)
        return JsonResponse({'success' : True, 'info' : ''})

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
                if not profile.is_verified:
                    x.succesful = False
                    x.save()
                    return JsonResponse({'success': False})
                x.succesful = True
                x.save()
                if profile not in visitors:
                    visitors.append(profile)
                for v in visitors:
                    print(v.user.first_name, v.user.last_name)
                login(request, user)
                return JsonResponse({'success': True})
        return JsonResponse({'success': False})
    
#Block of functions for queue managment    

def delete_visitor_view(request):
    if len(visitors) > 0:
        globals()['curVisitor'] = visitors.popleft()
    else:
        globals()['curVisitor'] = None
    return redirect('prof')

def pick_visitor_view(request, username):
    pickUser = User.objects.filter(username=username).first()
    pickProfile = Profile.objects.filter(user=pickUser).first()
    if pickProfile in visitors:
        tmpDeq = deque()
        tmpStudent = visitors.popleft()
        while tmpStudent != pickProfile:
            tmpDeq.append(tmpStudent)
            tmpStudent = visitors.popleft()
        globals()['curVisitor'] = tmpStudent
        while len(tmpDeq) > 0:
            tmpStudent = tmpDeq.pop()
            visitors.appendleft(tmpStudent)
    return redirect('prof')

def increment_view(request):
    globals()['counter'] += 1
    globals()['counter'] = globals()['counter'] % len(Profile.objects.filter(acc_type='Student').all())
    return redirect('prof')

def decrement_view(request):
    globals()['counter'] -= 1
    globals()['counter'] = globals()['counter'] % len(Profile.objects.filter(acc_type='Student').all())
    return redirect('prof')

def pick_button_view(request):
    students = Profile.objects.filter(acc_type='Student').all()
    username = str(students[globals()['counter']].user.username)
    return redirect('/pick_visitor/' + username)

#Block of functions for user registration

def mail_note_view(request):
    return render(request, 'mail_notification.html', {})

def send_mail_after_registration(email,token):
    subject = "Подтверждение почты для АСВТ EQC"
    message = f'Здравствуйте, перейдите по ссылке для верификации аккаунта http://127.0.0.1:8000/verify/{token}'
    email_from = EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message , email_from ,recipient_list)

def verify_view(request , auth_token):
    try:
        profile_obj = Profile.objects.filter(auth_token = auth_token).first()
        if profile_obj:
            profile_obj.is_verified = True
            profile_obj.save()
            return render(request, 'mail_success.html', {})
    except Exception as e:
        print(e)
        return render(request, 'failure.html', {})
    return render(request, 'failure.html', {})

def create_user_view(request):
    if is_ajax(request):
        email = request.POST.get('email')
        name = request.POST.get('name')
        surname = request.POST.get('surname')
        group = request.POST.get('group')
        password = "Qwerty715218"
        username = bio_to_username(name.lower(), surname.lower(), group.lower())
        
        if email not in allowed_mails:
            return JsonResponse({'success' : False, 'info' : 'Email not allowed'})
        
        photo = request.POST.get('photo')
        _, str_img = photo.split(';base64')
        decoded_file = base64.b64decode(str_img)
        try:        
            log = Log()
            log.photo.save('upload.png', ContentFile(decoded_file))
            log.save()
            
            res = classify_face(log.photo.path)
            if not res:
                return JsonResponse({'success' : False, 'info' : 'Face cannot be detected'})
            if res != "Unknown":
                return JsonResponse({'success' : False, 'info' : 'Your photo is already attached to some profile\nPlease contact the administrator'})
            
            if User.objects.filter(email = email).first():
              return JsonResponse({'success' : False, 'info' : 'Email is taken'})

            user_obj = User.objects.create(username = username, email=email, first_name=name, last_name=surname)
            user_obj.set_password(password)

            profile_obj = Profile.objects.filter(user = user_obj).first()#create(user = user_obj , token = str(uuid.uuid4))
            token = str(user_obj.id)
            profile_obj.auth_token = token
            profile_obj.photo.save('upload.png', ContentFile(decoded_file))
            profile_obj.save()
            send_mail_after_registration(email, token)
            return JsonResponse({'success' : True, 'info' : ''})
        except Exception as e:
            print(e)
            return JsonResponse({'success' : False, 'info' : 'Smth went wrong'})
    return JsonResponse({'success': False, 'info' : ''})