from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.hashers import make_password
from .models import *
import qrcode
import io
import base64
from django.utils.timezone import now
from datetime import datetime, timedelta
from datetime import datetime

def home(request):
    return render(request, 'index.html')

@login_required(login_url='/patient_login/')
def appointment_letter(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    qr_data = f"Appointment for {appointment.full_name}\nDate: {appointment.date}\nTime: {appointment.time.strftime('%I:%M %p')}\nDept: {appointment.department}"
    qr = qrcode.make(qr_data)
    buffer = io.BytesIO()
    qr.save(buffer, format='PNG')
    qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return render(request, 'appointment_letter.html', {
        'appointment': appointment,
        'qr_code': qr_base64
    })


@login_required(login_url='/patient_login/')
def patient_dashboard(request):
    today = now().date()
    current_time = now().time()

    # Upcoming appointments (today or later and not yet occurred)
    upcoming = Appointment.objects.filter(
        user=request.user
    ).filter(
        date__gt=today
    ) | Appointment.objects.filter(
        user=request.user,
        date=today,
        time__gte=current_time
    )

    # Completed appointments (past or today already occurred)
    completed = Appointment.objects.filter(
        user=request.user,
        date__lt=today
    ) | Appointment.objects.filter(
        user=request.user,
        date=today,
        time__lt=current_time
    )

    # Doctor availability data (add this too)
   

    context = {
        'appointments': upcoming.order_by('date', 'time')[:3],  # Only 3 upcoming preview
        'completed_appointments': completed.order_by('-date', '-time')[:3],  # Preview last 3 completed
        'upcoming_count': upcoming.count(),
        'completed_count': completed.count(),
        'user': request.user,
    }

    return render(request, 'patient_dashboard.html', context)



@login_required(login_url='/patient_login/')
def your_appointments_view(request):
    today = now().date()
    current_time = now().time()

    # Separate by date (and optionally time)
    upcoming_appointments = Appointment.objects.filter(
        user=request.user
    ).filter(
        date__gt=today  #date__gt -> date greater than 
    ) | Appointment.objects.filter(
        user=request.user,
        date=today,
        time__gte=current_time
    )
    
    completed_appointments = Appointment.objects.filter(
        user=request.user,
        date__lt=today
    ) | Appointment.objects.filter(
        user=request.user,
        date=today,
        time__lt=current_time
    )

    upcoming_appointments = upcoming_appointments.order_by('date', 'time')
    completed_appointments = completed_appointments.order_by('-date', '-time')

    return render(request, 'your_appointments.html', {
        'upcoming_appointments': upcoming_appointments,
        'completed_appointments': completed_appointments,
    })

def patient_signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        full_name = request.POST['full_name']
        email = request.POST['email']
        age = request.POST['age']
        contact = request.POST['contact']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already taken')
                return redirect('patient_signup')
            else:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=full_name
                )
                user.save()
                Profile.objects.create(user=user, contact_number=contact, age=age)
                messages.success(request, 'Account created successfully! Please log in.')
                return redirect('patient_login')
        else:
            messages.error(request, 'Passwords do not match')
            return redirect('patient_signup')

    return render(request, 'patient_signup.html')


def patient_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('patient_dashboard')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('patient_login')
    return render(request, 'patient_login.html')

@login_required(login_url='/patient_login/')
def logout(request):
    auth.logout(request)
    return redirect('home')


def appointment(request):
    return render(request,'appointment.html')


TIME_SLOTS = [
    '09:00 AM', '10:00 AM', '11:00 AM',
    '01:00 PM', '02:00 PM', '03:00 PM',
    '05:00 PM', '06:00 PM'
]

MAX_APPOINTMENTS_PER_DAY = len(TIME_SLOTS)
@login_required(login_url='/patient_login/')
def book_appointment(request):
    today = now().date()
    schedule = []

    for i in range(7):
        date = today + timedelta(days=i+1)
        day_name = date.strftime('%A')   #%A is a format code that returns the full weekday name. This line uses Python's strftime function to format a date object (date) into a string representing the day of the week.
        # formatted_date = date.strftime('%Y-%m-%d')
        formatted_date = date.strftime('%d-%m-%Y')

        if day_name == 'Sunday':
            status = 'closed'
        else:
            count = Appointment.objects.filter(date=date).count()
            status = 'full' if count >= MAX_APPOINTMENTS_PER_DAY else 'free'

        schedule.append({
            'day': day_name,
            'date': formatted_date,
            'status': status,
        })

    selected_day = request.POST.get('selected_date')
    selected_time = request.POST.get('selected_time')
    confirm = request.POST.get('confirm')
    slots = []
    booked_slots = []

    if selected_day:
        # selected_date_obj = datetime.strptime(selected_day, '%Y-%m-%d').date()
        selected_date_obj = datetime.strptime(selected_day, '%d-%m-%Y').date()
        booked_slots_qs = Appointment.objects.filter(date=selected_date_obj).values_list('time', flat=True)
        booked_slots = [t.strftime('%I:%M %p') for t in booked_slots_qs if t is not None]
        slots = TIME_SLOTS

    if request.method == 'POST' and confirm == 'yes':
        full_name = request.POST.get('full_name')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        department = request.POST.get('department')
        symptoms = request.POST.get('symptoms')  # ✅ New field

        if not selected_time:
            return render(request, 'book_appointment.html', {
                'days': schedule,
                'slots': slots,
                'booked_slots': booked_slots,
                'selected_day': selected_day,
                'selected_time': selected_time,
                'form_data': {
                    'full_name': full_name,
                    'contact': contact,
                    'email': email,
                    'department': department,
                    'symptoms': symptoms,
                },
                'error': 'Please select a valid time slot.'
            })

        selected_time_obj = datetime.strptime(selected_time, '%I:%M %p').time()
        # selected_date_obj = datetime.strptime(selected_day, '%Y-%m-%d').date()
        selected_date_obj = datetime.strptime(selected_day, '%d-%m-%Y').date()

        if Appointment.objects.filter(date=selected_date_obj, time=selected_time_obj).exists():
            return render(request, 'book_appointment.html', {
                'days': schedule,
                'slots': slots,
                'booked_slots': booked_slots,
                'selected_day': selected_day,
                'selected_time': selected_time,
                'form_data': {
                    'full_name': full_name,
                    'contact': contact,
                    'email': email,
                    'department': department,
                    'symptoms': symptoms,
                },
                'error': 'This time slot has just been booked. Please select another.'
            })

        appointment = Appointment.objects.create(
            full_name=full_name,
            contact=contact,
            email=email,
            date=selected_date_obj,
            time=selected_time_obj,
            department=department,
            symptoms=symptoms,  # ✅ Save new field
            user=request.user if request.user.is_authenticated else None
        )

        return redirect('appointment_letter', appointment_id=appointment.id)

    return render(request, 'book_appointment.html', {
        'days': schedule,
        'slots': slots,
        'booked_slots': booked_slots,
        'selected_day': selected_day,
        'selected_time': selected_time,
        'form_data': request.POST if request.method == 'POST' else {}
    })



@login_required(login_url='/patient_login')
def profile_view_edit(request):
    profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        contact_number = request.POST.get('contact_number')
        age = request.POST.get('age')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        form_valid = True
        password_updated = False

        # Password validation
        if new_password or confirm_password:
            if new_password != confirm_password:
                messages.error(request, '❌ Passwords do not match!')
                form_valid = False
            elif len(new_password) < 8:
                messages.error(request, '❌ Password must be at least 8 characters long!')
                form_valid = False
            else:
                request.user.password = make_password(new_password)
                request.user.save()
                password_updated = True

        if form_valid:
            # Only update profile if no errors
            profile.contact_number = contact_number
            profile.age = age
            profile.save()

            if password_updated:
                messages.success(request, '🔒 Password updated successfully!')
            messages.success(request, '✅ Profile updated successfully!')

            return redirect('profile_view_edit')

    return render(request, 'profile.html', {'profile': profile})




@login_required(login_url='/patient_login/')
def doctor_schedule(request):
    doctor_availability = {
        "General": {
            "Monday": "Dr. Smith",
            "Tuesday": "Dr. Emily",
            "Wednesday": "Dr. Smith",
            "Thursday": "Dr. Emily",
            "Friday": "Dr. Smith",
            "Saturday": "Dr. Emily",
            "Sunday": "Unavailable",
        },
        "Cardiology": {
            "Monday": "Dr. Anil",
            "Tuesday": "Dr. Kavya",
            "Wednesday": "Dr. Anil",
            "Thursday": "Dr. Kavya",
            "Friday": "Dr. Anil",
            "Saturday": "Dr. Kavya",
            "Sunday": "Unavailable",
        },
        "Neurology": {
            "Monday": "Dr. Rakesh",
            "Tuesday": "Dr. Sneha",
            "Wednesday": "Dr. Rakesh",
            "Thursday": "Dr. Sneha",
            "Friday": "Dr. Rakesh",
            "Saturday": "Dr. Sneha",
            "Sunday": "Unavailable",
        },
        "Orthopedics": {
            "Monday": "Dr. John",
            "Tuesday": "Dr. Neha",
            "Wednesday": "Dr. John",
            "Thursday": "Dr. Neha",
            "Friday": "Dr. John",
            "Saturday": "Dr. Neha",
            "Sunday": "Unavailable",
        },
        "Pediatrics": {
            "Monday": "Dr. Ritu",
            "Tuesday": "Dr. Mohan",
            "Wednesday": "Dr. Ritu",
            "Thursday": "Dr. Mohan",
            "Friday": "Dr. Ritu",
            "Saturday": "Dr. Mohan",
            "Sunday": "Unavailable",
        },
    }

    selected_department = request.GET.get('department', 'General')
    schedule = doctor_availability.get(selected_department, {})

    context = {
        'doctor_availability': doctor_availability,
        'selected_department': selected_department,
        'schedule': schedule,
    }
    return render(request, 'doctor_schedule.html', context)
