from django.urls import path
from . import views
urlpatterns=[
    path('',views.home,name='home'),
    path('patient_login',views.patient_login,name='patient_login'),
    path('patient_signup',views.patient_signup,name='patient_signup'),
    path('patient_dashboard', views.patient_dashboard, name='patient_dashboard'),
    path('appointment', views.appointment, name='appointment'),
    path('logout', views.logout, name='logout'),
    path('book_appointment', views.book_appointment, name='book_appointment'),
    path('your_appointments_view', views.your_appointments_view, name='your_appointments_view'),
    path('appointment_letter/<int:appointment_id>/', views.appointment_letter, name='appointment_letter'), #/<int:appointment_id>/
    path('profile_view_edit', views.profile_view_edit, name='profile_view_edit'),
    path('doctor_schedule', views.doctor_schedule, name='doctor_schedule'),


    
]