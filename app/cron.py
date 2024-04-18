


import logging
import time
from app.utils import send_checkout_reminder_email
from app.models import Employee
from django.core.management.base import BaseCommand
from django.utils import timezone

logger = logging.getLogger('django')

def notification():
    logger.info('Cron job was called')
    employees = Employee.objects.filter(is_active=True)
    current_time = timezone.localtime(timezone.now())
    current_date = current_time.date()  # Get the current date
    
    for employee in employees:
        checkin_time = timezone.localtime(employee.check_in)
        log_date = checkin_time.date()  # Get the date of the log entry
        
        if log_date == current_date:  # Check if the log entry is for the current day
            logger.info(f"Current time: {current_time}")
            logger.info(f"Checkin time: {checkin_time}")
            
            duration_hours = (current_time - checkin_time).total_seconds() / 3600
            logger.info(f"Duration time: {duration_hours}")
            
            if duration_hours >= 8:
                logger.info(f"Cron job ran for {duration_hours} hours, exceeding the base threshold of hours.")
                send_checkout_reminder_email(employee)


