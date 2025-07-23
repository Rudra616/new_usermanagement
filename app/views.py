from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.paginator import Paginator
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from django.conf import settings
from django.contrib import messages
from .models import User, District, State
import uuid, random
from django.middleware.csrf import get_token
# get_token: Creates or retrieves CSRF token.

from django.views.decorators.csrf import csrf_protect
# Skips CSRF check for certain views (SPA POST requests).
from django.utils.decorators import method_decorator

from django.views.decorators.http import require_POST
# @method_decorator(csrf_exempt, name='dispatch')

class UserManagementView(View):
        # -------------------- Dynamic SPA Router --------------------
    def logout(self, request):
        request.session.flush()  # logout user by clearing session

        # Ensure CSRF cookie is set on response
        get_token(request)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Logged out successfully.',
                'redirect': '/app/'
            })
        return redirect('/app/')

    def spa_router(self, request, page="home",**kwargs):
        token = kwargs.get('token')

        print(f"spa_router called with page: {page}")
        csrf_token = get_token(request)
        context = {
            'csrf_token': csrf_token,
        }
    
        # Handle CAPTCHA refresh via AJAX
        if request.GET.get('refresh_captcha'):
            new_captcha = self.generate_captcha()
            request.session['captcha_code'] = new_captcha
            return JsonResponse({'captcha': new_captcha})
    
        # Handle POST requests for login, register, update_profile, forgot-password, reset-password
        if page == "login" and request.method == 'POST':
            return self.login(request)
        elif page == "register" and request.method == 'POST':
            return self.register(request)
        elif page == "update_profile" and request.method == 'POST':
            return self.update_profile(request)
        elif page == "forgot-password" and request.method == 'POST':
            return self.forgot_password_view(request)
        elif page == "reset-password" and request.method == 'POST':
            return self.reset_password_view(request, token)
    
        if page == "reset-password":
            context['token'] = token
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    html = render_to_string('reset_password.html', context=context, request=request)
                    return JsonResponse({'html': html})
            return render(request, 'index.html', context=context)


        # Validate requested page
        valid_pages = [
            "home", "about", "feature", "service", "team", "testimonial",
            "appoinment", "contact", "login", "register", "update_profile",
            "admin", "forgot-password", "reset-password", "404"
        ]
    
        if page not in valid_pages:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('404.html', request=request)
                return JsonResponse({'html': html,'message': 'not valid page'})
            return render(request, '404.html', status=404)
    
        # Prepare context for certain pages
        if page == "login":
            captcha_code = self.generate_captcha()
            request.session['captcha_code'] = captcha_code
            context['captcha_code'] = captcha_code
    
        if page == "register":
            context['states'] = State.objects.all()
    
        if page == "update_profile":
            userName = request.session.get('userName')
            if userName:
                user = User.objects.filter(userName=userName).first()
                context['username'] = user
                context['states'] = State.objects.all()
                context['districts'] = District.objects.filter(state=user.state) if user and user.state else District.objects.none()
            else:
                # If not logged in, redirect to login
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    html = render_to_string('login.html', request=request)
                    return JsonResponse({'html': html,'message': 'login page',})
                return redirect('spa_router', page='login')

        if page == "admin" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
            if request.GET.get('search') or request.GET.get('per_page') or request.GET.get('page'):
                return self.admin_dashboard(request)


        # For AJAX requests, render only the page template and return as JSON
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string(f'{page}.html', context=context, request=request)
            return JsonResponse({'html': html,'message': 'successfully work',})
    
        # For normal requests, render the SPA container page (index.html)
        return render(request, 'index.html', context=context)
    
    def navbar(self, request):
        html = render_to_string('nav.html', request=request)
        return JsonResponse({'html': html,'message':'navbar'})

    
    # -------------------- Helper --------------------
    def generate_captcha(self):
        return str(random.randint(1000, 9999))

    def refresh_captcha(self,request):
        if request.method == 'GET':
            new_captcha = self.generate_captcha()
            request.session['captcha_code'] = new_captcha
            return JsonResponse({
                'captcha': new_captcha,
                'captcha_code': new_captcha  # For compatibility
            })
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
                
                if image :
                    # Get original file extension (e.g., .jpg or .png)
                    extension = image.name.split('.')[-1]
                    timestemp = timezone.now().strftime("%y-%m-%d_%H-%M-%S")
                    # Create new filename: username_YYYY-MM-DD_HH-MM-SS.ext
                    new_filename = f"{username}_{timestemp}.{extension}"
                    print(new_filename)
                    image.name = new_filename

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
                return JsonResponse({'html': html,'message':'ragister page'})
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
            return redirect('spa_router', page='home')  # Redirect to home for invalid

        if user_obj.is_varified:
            messages.info(request, "Your email is already verified.")
        else:
            user_obj.is_varified = True
            user_obj.email_verification_token = None
            user_obj.save()
            messages.success(request, "Your email has been verified. Welcome!")

            # OPTIONAL: Log user in after verification
            request.session['userName'] = user_obj.userName

        return redirect('spa_router', page='home')  # Redirect verified user to home



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
            request.session['userRole'] = user_obj.role

            redirect_page = 'admin' if user_obj.role == 'admin' else 'home'

            # For AJAX requests (SPA)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                template = 'admin.html' if user_obj.role == 'admin' else 'home.html'
                if user_obj.role == 'admin':
                    context = {
                        'userdetails': user_obj,
                        'search_query': '',
                        'per_page': 10
                    }
                else:
                    context = {}

                html = render_to_string(template, context, request=request)
                return JsonResponse({
                    'success': True,
                    'html': html,
                    'redirect_page': redirect_page,
                    'userName': user_obj.userName,  
                    'user_role': user_obj.role  # Optional: for frontend customization
                })

            # For traditional form submission (fallback)
            return redirect("spa_roter",redirect_page)

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
    # @csrf_exempt
    def update_profile(self, request):
        if request.method == "POST":
            userName = request.session.get("userName")
            user = get_object_or_404(User, userName=userName)

            # Check if username is changing and if it's already taken
            new_username = request.POST.get("username", "").strip()
            if new_username and new_username != user.userName:
                if User.objects.filter(userName=new_username).exclude(id=user.id).exists():
                    return JsonResponse({
                        "success": False,
                        "message": "This username is already taken. Please try another one."
                    })
                else:
                    messages.error(request, "This username is already taken.")
                    return redirect("spa_router", page="update_profile")
            user.userName = new_username

            # Update other fields
            user.firstName = request.POST.get("first_name", "").strip()
            user.lastName = request.POST.get("last_name", "").strip()
            user.email = request.POST.get("email", "").strip()
            user.address = request.POST.get("address", "").strip()
            user.phoneNumber = request.POST.get("phone_number", "").strip()
            user.dateOfBirth = request.POST.get("date_of_birth") or None

            state_id = request.POST.get("state")
            district_id = request.POST.get("district")
            user.state = State.objects.get(id=state_id) if state_id else None
            user.district = District.objects.get(id=district_id) if district_id else None

            if request.FILES.get("image"):
                user.image = request.FILES["image"]

            user.save()

            # Refresh user data for context
            user.refresh_from_db()
            states = State.objects.all()
            districts = District.objects.filter(state=user.state) if user.state else District.objects.none()

            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                html = render_to_string("update_profile.html", {
                    "username": user,
                    "states": states,
                    "districts": districts
                }, request=request)
                return JsonResponse({
                    "success": True,
                    "message": "Profile updated successfully!",
                    "html": html
                })

        return redirect("spa_router", page="update_profile")

    def admin_dashboard(self, request):
        user_obj = User.objects.get(userName=request.session.get('userName'))
        if user_obj.role != 'admin':
            return redirect('spa_router', page='home')

        all_users = User.objects.filter(role='user')
        search_query = request.GET.get('search', '')
        if search_query:
            all_users = all_users.filter(userName__icontains=search_query)

        per_page = request.GET.get('per_page', '10')
        if per_page == 'all':
            per_page = all_users.count() or 1  # Show all users
        else:
            try:
                per_page = int(per_page)
            except ValueError:
                per_page = 10  # fallback

        paginator = Paginator(all_users, per_page)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            users_list = []
            for user in page_obj:
                users_list.append({
                    'id': user.id,
                    'first_name': user.firstName,
                    'last_name': user.lastName,
                    'username': user.userName,
                    'email': user.email,
                    'address': user.address,
                    'district': user.district.name if user.district else '',
                    'state': user.state.name if user.state else '',
                    'date_of_birth': user.dateOfBirth.strftime('%Y-%m-%d') if user.dateOfBirth else None
                })

            return JsonResponse({
                'success': True,
                'users': users_list,
                'pagination': {
                    'current_page': page_obj.number,
                    'total_pages': paginator.num_pages,
                    'has_previous': page_obj.has_previous(),
                    'has_next': page_obj.has_next()
                },
                'search_count': all_users.count()
            })
        context = {
            'userdetails': user_obj,
            'page_obj': page_obj,
            'search_query': search_query,
            'per_page': request.GET.get('per_page', '10'),
        }
        return render(request, 'admin.html', context)

    # @csrf_exempt    
    def delete_user(self,request, user_id):
        if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                user = get_object_or_404(User, pk=user_id)
                user.delete()
                return JsonResponse({'success': True, 'message': 'User deleted'})
            except Exception as e:
                return JsonResponse({'success': False, 'message': str(e)})
        return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)
    # -------------------- Password Reset --------------------
    def forgot_password_view(self, request):
        print("helo")
        if request.method == 'POST':
            username = request.POST.get('username')
            user = User.objects.filter(userName=username).first()
            if user:
                token = uuid.uuid4()
                user.reset_token = token
                user.reset_expire = timezone.now() + timezone.timedelta(hours=1)
                user.save()
                reset_link = request.build_absolute_uri(f'/app/reset-password/{token}/')
                send_mail(
                    'Password Reset',
                    f'Reset your password: {reset_link}',
                    settings.EMAIL_HOST_USER,
                    [user.email]
                )
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': "If username exists, a reset link has been sent to the email."})
            else:
                messages.info(request, "If username exists, a reset link has been sent to the email.")
                return redirect('spa_router', page='login')  # fallback for normal POST

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
    
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': 'Password reset successful. You can now log in.',
                        'redirect_url': '/app/login/'
                    })
                else:
                    messages.success(request, "Password reset successful. You can now log in.")
                    return redirect('spa_router', page='login')
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'message': 'Passwords do not match.'})
                else:
                    messages.error(request, 'Passwords do not match.')
    
        # For GET or failed POST, render reset-password form template with token in context
        context = {
            'token': token,
            'csrf_token': get_token(request),
        }
        html = render_to_string('reset-password.html', context=context, request=request)
    
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Return partial HTML for SPA AJAX load
            return JsonResponse({'html': html})
        else:
            # Full page load fallback (if someone visits URL directly)
            return render(request, 'reset-password.html', context=context)
