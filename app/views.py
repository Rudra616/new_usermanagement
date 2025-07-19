# from django.views import View
# from django.shortcuts import render, redirect, get_object_or_404
# from django.http import JsonResponse
# from django.contrib.auth.hashers import make_password, check_password
# from django.core.mail import EmailMultiAlternatives, send_mail
# from django.template.loader import render_to_string
# from django.utils.html import strip_tags
# from django.core.paginator import Paginator
# from django.utils import timezone
# from django.conf import settings
# from django.contrib import messages
# from .models import User, District, State
# import uuid, random

# class UserManagementView(View):
#     def navbar(self, request):
#         html = render_to_string('nav.html', request=request)
#         return JsonResponse({'html': html})

#     # -------------------- Static Pages --------------------
#     def index(self, request, *args, **kwargs):
#         if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#             html = render(request, 'index.html').content.decode('utf-8')
#             return JsonResponse({'html': html})
#         else:
#             return render(request, 'index.html')

#     def home(self, request):
#         if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#             html = render_to_string('home.html', request=request)
#             return JsonResponse({'html': html})
#         return render(request, 'index.html')

#     def about(self, request):
#         if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#             html = render_to_string('about.html', request=request)
#             return JsonResponse({'html': html})
#         return render(request, 'index.html')

#     def feature(self, request):
#         if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#             html = render_to_string('feature.html', request=request)
#             return JsonResponse({'html': html})
#         return render(request, 'index.html')

#     def service(self, request):
#         if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#             html = render_to_string('service.html', request=request)
#             return JsonResponse({'html': html})
#         return render(request, 'index.html')

#     def team(self, request):
#         if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#             html = render_to_string('team.html', request=request)
#             return JsonResponse({'html': html})
#         return render(request, 'index.html')

#     def testimonial(self, request):
#         if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#             html = render_to_string('testimonial.html', request=request)
#             return JsonResponse({'html': html})
#         return render(request, 'index.html')

#     def appoinment(self, request):
#         if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#             html = render_to_string('appoinment.html', request=request)
#             return JsonResponse({'html': html})
#         return render(request, 'index.html')

#     def error(self, request):
#         if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#             html = render_to_string('404.html', request=request)
#             return JsonResponse({'html': html})
#         return render(request, 'index.html')

#     def contact(self, request):
#         if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#             html = render_to_string('contact.html', request=request)
#             return JsonResponse({'html': html})
#         return render(request, 'index.html')

#     # -------------------- Helper --------------------
#     def generate_captcha(self):
#         return str(random.randint(1000, 9999))

#     def refresh_captcha(self, request):
#         new_captcha = self.generate_captcha()
#         request.session['captcha_code'] = new_captcha
#         return JsonResponse({'captcha': new_captcha})

#     # -------------------- Registration --------------------
#     def register(self, request):
#         if request.method == 'POST':
#             first_name = request.POST.get('first_name', '').strip()
#             last_name = request.POST.get('last_name', '').strip()
#             username = request.POST.get('username', '').strip()
#             email = request.POST.get('email', '').strip()
#             password = request.POST.get('password', '').strip()
#             address = request.POST.get('address', '').strip()
#             district_id = request.POST.get('district', '').strip()
#             state_id = request.POST.get('state', '').strip()
#             phone_number = request.POST.get('phone_number', '').strip()
#             image = request.FILES.get('image')
#             date_of_birth = request.POST.get('date_of_birth', '').strip()

#             if not all([first_name, last_name, username, password, email, address, district_id, state_id, phone_number, date_of_birth]):
#                 return JsonResponse({'success': False, 'error': 'All fields are required.'})

#             if User.objects.filter(userName=username).exists():
#                 return JsonResponse({'success': False, 'message': 'Username already taken.'})

#             try:
#                 state = State.objects.get(id=state_id)
#                 district = District.objects.get(id=district_id)
#             except (State.DoesNotExist, District.DoesNotExist):
#                 return JsonResponse({'success': False, 'error': 'Invalid State or District.'})

#             email_verification_token = uuid.uuid4()

#             try:
#                 user = User.objects.create(
#                     firstName=first_name,
#                     lastName=last_name,
#                     userName=username,
#                     password=make_password(password),
#                     email=email,
#                     address=address,
#                     state=state,
#                     district=district,
#                     phoneNumber=phone_number,
#                     image=image if image else None,
#                     dateOfBirth=date_of_birth,
#                     email_verification_token=email_verification_token,
#                     is_varified=False
#                 )
#                 verification_link = request.build_absolute_uri(f'/app/verify/{email_verification_token}/')
#                 html_content = render_to_string('email.html', {'verification_link': verification_link, 'username': username})
#                 plain_message = strip_tags(html_content)
#                 subject = 'Email Verification'
#                 from_email = settings.EMAIL_HOST_USER
#                 to_email = [user.email]

#                 email_message = EmailMultiAlternatives(subject, plain_message, from_email, to_email)
#                 email_message.attach_alternative(html_content, 'text/html')
#                 email_message.send()

#                 return JsonResponse({'success': True, 'message': 'User registered successfully. Check your email to verify your account.'})

#             except Exception as e:
#                 print(f"Error: {e}")
#                 return JsonResponse({'success': False, 'error': 'Could not save user or send email.'})

#         states = State.objects.all()
#         if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#             html = render_to_string('reg_user.html', {'states': states}, request=request)
#             return JsonResponse({'html': html})
#         return render(request, 'index.html')

#     def get_districts(self, request):
#         state_id = request.GET.get('state_id')
#         if not state_id:
#             return JsonResponse([], safe=False)
#         districts = District.objects.filter(state_id=state_id).values('id', 'name')
#         return JsonResponse(list(districts), safe=False)

#     def verify_email(self, request, token):
#         try:
#             user_obj = User.objects.get(email_verification_token=token)
#         except User.DoesNotExist:
#             messages.error(request, "Invalid or expired verification link.")
#             return redirect('login')

#         if user_obj.is_varified:
#             messages.info(request, "Your email is already verified.")
#         else:
#             user_obj.is_varified = True
#             user_obj.email_verification_token = None
#             user_obj.save()
#             messages.success(request, "Your email has been verified. You can now log in.")
#         return redirect('login')

#     # -------------------- Login --------------------
#     def login(self, request):
#         if request.method == 'POST':
#             userName = request.POST.get('name', '').strip()
#             password = request.POST.get('password', '').strip()
#             entered_captcha = request.POST.get('captcha', '').strip()
#             saved_captcha = request.session.get('captcha_code')

#             # Validate captcha first
#             if entered_captcha != saved_captcha:
#                 new_captcha = self.generate_captcha()
#                 request.session['captcha_code'] = new_captcha
#                 return JsonResponse({'success': False, 'message': 'Invalid captcha.', 'captcha': new_captcha})

#             user_obj = User.objects.filter(userName=userName).first()
#             new_captcha = self.generate_captcha()
#             request.session['captcha_code'] = new_captcha

#             if not user_obj:
#                 return JsonResponse({'success': False, 'message': 'Username not found.', 'captcha': new_captcha})
#             if not check_password(password, user_obj.password):
#                 return JsonResponse({'success': False, 'message': 'Wrong password.', 'captcha': new_captcha})
#             if not user_obj.is_varified:
#                 return JsonResponse({'success': False, 'message': 'Please verify your email first.', 'captcha': new_captcha})

#             # Save session
#             request.session['userName'] = user_obj.userName
#             redirect_url = '/app/admin-dashboard/' if user_obj.role == 'admin' else '/app/'

#             if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#                 # Render dashboard/home directly and send back
#                 if user_obj.role == 'admin':
#                     html = render_to_string('admin.html', request=request)
#                 else:
#                     html = render_to_string('home.html', request=request)
#                 return JsonResponse({'success': True, 'html': html, 'redirect_url': redirect_url})
#             else:
#                 return redirect(redirect_url)

#         # GET → render login page
#         captcha_code = self.generate_captcha()
#         request.session['captcha_code'] = captcha_code

#         if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#             html = render_to_string('login.html', {'captcha_code': captcha_code}, request=request)
#             return JsonResponse({'success': True, 'html': html})
#         else:
#             return render(request, 'index.html')

#     # -------------------- Profile --------------------
#     def update_profile(self, request):
#     #       
#     # Handles profile update via AJAX.
#     # Accepts POST requests and updates the user model.
#     # 
#         if request.method == 'POST':
#             userName = request.session.get('userName')
#             user = User.objects.get(userName=userName)
#             user.firstName = request.POST.get('first_name', '').strip()
#             user.lastName = request.POST.get('last_name', '').strip()
#             user.email = request.POST.get('email', '').strip()
#             user.address = request.POST.get('address', '').strip()
#             user.phoneNumber = request.POST.get('phone_number', '').strip()
#             dateOfBirth = request.POST.get('date_of_birth', '').strip()
#             if dateOfBirth:
#                 user.dateOfBirth = dateOfBirth
#             state_id = request.POST.get('state')
#             district_id = request.POST.get('district')
#             if state_id:
#                 user.state_id = state_id
#             if district_id:
#                 user.district_id = district_id
#             image = request.FILES.get('image')
#             if image:
#                 user.image = image
#             user.save()
#             return JsonResponse({'success': True, 'message': 'Profile updated successfully.'})

#         user = User.objects.get(userName=request.session['userName'])
#         states = State.objects.all()
#         districts = District.objects.filter(state=user.state) if user.state else District.objects.none()
#         if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#             html = render_to_string('update_profile.html', {'username': user, 'states': states, 'districts': districts}, request=request)
#             return JsonResponse({'html': html})
#         return render(request, 'index.html')

#     def logout(self, request):
#         if 'userName' in request.session:
#             del request.session['userName']
#         return redirect('index')

#     # -------------------- Admin --------------------
#     def admin_dashboard(self, request):
#         user_obj = User.objects.get(userName=request.session.get('userName'))
#         if user_obj.role != 'admin':
#             return redirect('index')

#         all_users = User.objects.filter(role='user')
#         search_query = request.GET.get('search', '')
#         if search_query:
#             all_users = all_users.filter(userName__icontains=search_query)
#         per_page = request.GET.get('per_page', 10)
#         paginator = Paginator(all_users, per_page)
#         page_number = request.GET.get('page', 1)
#         page_obj = paginator.get_page(page_number)

#         if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#             html = render_to_string('admin.html', {'page_obj': page_obj, 'search_query': search_query, 'per_page': per_page}, request=request)
#             return JsonResponse({'html': html})
#         return render(request, 'index.html')

#     def delete_user(self, request, id):
#         User.objects.filter(id=id).delete()
#         return JsonResponse({'success': True, 'message': 'User deleted successfully.'})

#     # -------------------- Password Reset --------------------
#     def forgot_password_view(self, request):
#         if request.method == 'POST':
#             username = request.POST.get('username')
#             user = User.objects.filter(userName=username).first()
#             if user:
#                 token = uuid.uuid4()
#                 user.reset_token = token
#                 user.reset_expire = timezone.now() + timezone.timedelta(hours=1)
#                 user.save()
#                 reset_link = request.build_absolute_uri(f'/app/reset-password/{token}/')
#                 send_mail('Password Reset', f'Reset your password: {reset_link}', settings.EMAIL_HOST_USER, [user.email])
#             messages.info(request, "If username exists, a reset link has been sent to the email.")
#         if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#             html = render_to_string('forgot_password.html', request=request)
#             return JsonResponse({'html': html})
#         return render(request, 'index.html')

#     def reset_password_view(self, request, token):
#         user = get_object_or_404(User, reset_token=token, reset_expire__gt=timezone.now())
#         if request.method == 'POST':
#             password = request.POST.get('password')
#             confirm = request.POST.get('confirm_password')
#             if password == confirm:
#                 user.password = make_password(password)
#                 user.reset_token = None
#                 user.reset_expire = None
#                 user.save()
#                 return JsonResponse({'success': True, 'message': 'Password reset successful. You can now log in.'})
#             else:
#                 return JsonResponse({'success': False, 'message': 'Passwords do not match.'})
#         html = render_to_string('reset_password.html', request=request)
#         return JsonResponse({'html': html})


from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.paginator import Paginator
from django.utils import timezone
from django.conf import settings
from django.contrib import messages
from .models import User, District, State
import uuid, random


class UserManagementView(View):
    # -------------------- Dynamic SPA Router --------------------
    def spa_router(self, request, page="home"):
        """
        Dynamically serve partials for AJAX and index.html for direct browser hits.
        """
        # Handle POST requests for login
        if page == "login" and request.method == 'POST':
            return self.login(request)  # Call your existing login method

        valid_pages = [
            "home", "about", "feature", "service", "team", "testimonial",
            "appoinment", "contact", "login", "register", "update_profile",
            "admin-dashboard", "forgot-password", "reset-password", "404"
        ]

        if page not in valid_pages:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('404.html', request=request)
                return JsonResponse({'html': html})
            return render(request, '404.html', status=404)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string(f'{page}.html', request=request)
            return JsonResponse({'html': html})
        return render(request, 'index.html')
    # -------------------- Navbar --------------------
    def navbar(self, request):
        html = render_to_string('nav.html', request=request)
        return JsonResponse({'html': html})

    # -------------------- Helper --------------------
    def generate_captcha(self):
        return str(random.randint(1000, 9999))

    def refresh_captcha(self, request):
        new_captcha = self.generate_captcha()
        request.session['captcha_code'] = new_captcha
        return JsonResponse({'captcha': new_captcha})

    # -------------------- Registration --------------------
    def register(self, request):
        if request.method == 'POST':
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            username = request.POST.get('username', '').strip()
            email = request.POST.get('email', '').strip()
            password = request.POST.get('password', '').strip()
            address = request.POST.get('address', '').strip()
            district_id = request.POST.get('district', '').strip()
            state_id = request.POST.get('state', '').strip()
            phone_number = request.POST.get('phone_number', '').strip()
            image = request.FILES.get('image')
            date_of_birth = request.POST.get('date_of_birth', '').strip()

            if not all([first_name, last_name, username, password, email, address, district_id, state_id, phone_number, date_of_birth]):
                return JsonResponse({'success': False, 'error': 'All fields are required.'})

            if User.objects.filter(userName=username).exists():
                return JsonResponse({'success': False, 'message': 'Username already taken.'})

            try:
                state = State.objects.get(id=state_id)
                district = District.objects.get(id=district_id)
            except (State.DoesNotExist, District.DoesNotExist):
                return JsonResponse({'success': False, 'error': 'Invalid State or District.'})

            email_verification_token = uuid.uuid4()

            try:
                user = User.objects.create(
                    firstName=first_name,
                    lastName=last_name,
                    userName=username,
                    password=make_password(password),
                    email=email,
                    address=address,
                    state=state,
                    district=district,
                    phoneNumber=phone_number,
                    image=image if image else None,
                    dateOfBirth=date_of_birth,
                    email_verification_token=email_verification_token,
                    is_varified=False
                )
                verification_link = request.build_absolute_uri(f'/app/verify/{email_verification_token}/')
                html_content = render_to_string('email.html', {'verification_link': verification_link, 'username': username})
                plain_message = strip_tags(html_content)
                subject = 'Email Verification'
                from_email = settings.EMAIL_HOST_USER
                to_email = [user.email]

                email_message = EmailMultiAlternatives(subject, plain_message, from_email, to_email)
                email_message.attach_alternative(html_content, 'text/html')
                email_message.send()

                return JsonResponse({'success': True, 'message': 'User registered successfully. Check your email to verify your account.'})

            except Exception as e:
                print(f"Error: {e}")
                return JsonResponse({'success': False, 'error': 'Could not save user or send email.'})

        states = State.objects.all()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('register.html', {'states': states}, request=request)
            return JsonResponse({'html': html})
        return render(request, 'index.html')

    def get_districts(self, request):
        state_id = request.GET.get('state_id')
        if not state_id:
            return JsonResponse([], safe=False)
        districts = District.objects.filter(state_id=state_id).values('id', 'name')
        return JsonResponse(list(districts), safe=False)

    def verify_email(self, request, token):
        try:
            user_obj = User.objects.get(email_verification_token=token)
        except User.DoesNotExist:
            messages.error(request, "Invalid or expired verification link.")
            return redirect('spa_router', page='login')

        if user_obj.is_varified:
            messages.info(request, "Your email is already verified.")
        else:
            user_obj.is_varified = True
            user_obj.email_verification_token = None
            user_obj.save()
            messages.success(request, "Your email has been verified. You can now log in.")
        return redirect('spa_router', page='login')

        # -------------------- Login --------------------
    def login(self, request):
        if request.method == 'POST':
            userName = request.POST.get('name', '').strip()
            password = request.POST.get('password', '').strip()
            entered_captcha = request.POST.get('captcha', '').strip()
            saved_captcha = request.session.get('captcha_code')

            # Debug logging
            print(f"Login attempt - User: {userName}, Captcha: {entered_captcha} (Expected: {saved_captcha})")

            # Validate captcha first
            if entered_captcha != saved_captcha:
                new_captcha = self.generate_captcha()
                request.session['captcha_code'] = new_captcha
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid captcha.',
                    'captcha': new_captcha,
                    'captcha_code': new_captcha  # For compatibility
                })

            user_obj = User.objects.filter(userName=userName).first()
            new_captcha = self.generate_captcha()
            request.session['captcha_code'] = new_captcha

            if not user_obj:
                return JsonResponse({
                    'success': False,
                    'message': 'Username not found.',
                    'captcha': new_captcha
                })

            if not check_password(password, user_obj.password):
                return JsonResponse({
                    'success': False,
                    'message': 'Wrong password.',
                    'captcha': new_captcha
                })

            if not user_obj.is_varified:
                return JsonResponse({
                    'success': False,
                    'message': 'Please verify your email first.',
                    'captcha': new_captcha
                })

            # Login successful
            request.session['userName'] = user_obj.userName
            redirect_url = '/app/admin-dashboard/' if user_obj.role == 'admin' else '/app/'

            # For AJAX requests (SPA)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                template = 'admin.html' if user_obj.role == 'admin' else 'home.html'
                html = render_to_string(template, request=request)
                return JsonResponse({
                    'success': True,
                    'html': html,
                    'redirect_url': redirect_url,
                    'user_role': user_obj.role  # Optional: for frontend customization
                })

            # For traditional form submission (fallback)
            return redirect(redirect_url)

        # GET request - render login page
        captcha_code = self.generate_captcha()
        request.session['captcha_code'] = captcha_code

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('login.html', {
                'captcha_code': captcha_code
            }, request=request)
            return JsonResponse({
                'success': True,
                'html': html,
                'is_login_page': True  # Flag for frontend
            })

        # Traditional GET request
        return render(request, 'index.html')
    # -------------------- Profile --------------------
    def update_profile(self, request):
        if request.method == 'POST':
            userName = request.session.get('userName')
            user = User.objects.get(userName=userName)
            user.firstName = request.POST.get('first_name', '').strip()
            user.lastName = request.POST.get('last_name', '').strip()
            user.email = request.POST.get('email', '').strip()
            user.address = request.POST.get('address', '').strip()
            user.phoneNumber = request.POST.get('phone_number', '').strip()
            dateOfBirth = request.POST.get('date_of_birth', '').strip()
            if dateOfBirth:
                user.dateOfBirth = dateOfBirth
            state_id = request.POST.get('state')
            district_id = request.POST.get('district')
            if state_id:
                user.state_id = state_id
            if district_id:
                user.district_id = district_id
            image = request.FILES.get('image')
            if image:
                user.image = image
            user.save()
            return JsonResponse({'success': True, 'message': 'Profile updated successfully.'})

        user = User.objects.get(userName=request.session['userName'])
        states = State.objects.all()
        districts = District.objects.filter(state=user.state) if user.state else District.objects.none()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('update_profile.html', {'username': user, 'states': states, 'districts': districts}, request=request)
            return JsonResponse({'html': html})
        return render(request, 'index.html')

    def logout(self, request):
        request.session.flush()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # For AJAX requests, return redirect info
            return JsonResponse({
                'success': True,
                'message': 'Logged out successfully.',
                'redirect': '/app/'  # Redirect to home page
            })
        # Fallback for non-AJAX requests
        return redirect('/app/')
    # -------------------- Admin --------------------
    def admin_dashboard(self, request):
        user_obj = User.objects.get(userName=request.session.get('userName'))
        if user_obj.role != 'admin':
            return redirect('spa_router', page='home')

        all_users = User.objects.filter(role='user')
        search_query = request.GET.get('search', '')
        if search_query:
            all_users = all_users.filter(userName__icontains=search_query)
        per_page = request.GET.get('per_page', 10)
        paginator = Paginator(all_users, per_page)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('admin.html', {'page_obj': page_obj, 'search_query': search_query, 'per_page': per_page}, request=request)
            return JsonResponse({'html': html})
        return render(request, 'index.html')

    def delete_user(self, request, id):
        User.objects.filter(id=id).delete()
        return JsonResponse({'success': True, 'message': 'User deleted successfully.'})

    # -------------------- Password Reset --------------------
    def forgot_password_view(self, request):
        if request.method == 'POST':
            username = request.POST.get('username')
            user = User.objects.filter(userName=username).first()
            if user:
                token = uuid.uuid4()
                user.reset_token = token
                user.reset_expire = timezone.now() + timezone.timedelta(hours=1)
                user.save()
                reset_link = request.build_absolute_uri(f'/app/reset-password/{token}/')
                send_mail('Password Reset', f'Reset your password: {reset_link}', settings.EMAIL_HOST_USER, [user.email])
            messages.info(request, "If username exists, a reset link has been sent to the email.")
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('forgot_password.html', request=request)
            return JsonResponse({'html': html})
        return render(request, 'index.html')

    def reset_password_view(self, request, token):
        user = get_object_or_404(User, reset_token=token, reset_expire__gt=timezone.now())
        if request.method == 'POST':
            password = request.POST.get('password')
            confirm = request.POST.get('confirm_password')
            if password == confirm:
                user.password = make_password(password)
                user.reset_token = None
                user.reset_expire = None
                user.save()
                return JsonResponse({'success': True, 'message': 'Password reset successful. You can now log in.'})
            else:
                return JsonResponse({'success': False, 'message': 'Passwords do not match.'})
        html = render_to_string('reset_password.html', request=request)
        return JsonResponse({'html': html})
