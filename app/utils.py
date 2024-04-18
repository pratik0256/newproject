from django.core.mail import send_mail
from app.models import Employee

def send_checkout_reminder_email(employee):
    subject = 'Reminder: Check Out'
    # Accessing the email from the associated CustomUser
    user_email = employee.user.email
    message = f'Dear {employee.user.employee_name},\n\nYou have not checked out for 8 hours or more. Please remember to check out.\n\nBest regards,\nYour Company'
    send_mail(subject, message, '19ce039@gardividyapith.ac.in', [user_email])
