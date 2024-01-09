from django_cron import CronJobBase, Schedule
from myapp.models import Rental,Notification
from django.utils import timezone 
from django.contrib import messages


class NotifyRentedUsersJob(CronJobBase):
    RUN_EVERY_MINS = 1 # run every minute
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'myapp.cron.NotifyRentedUsersJob'
    def do(self):
        
        # fetch those rented notifications who has 3 days left
        rented_books = Rental.objects.filter(return_date__lte=timezone.now() + timezone.timedelta(days=3),
                                             returned=False)
        for rental in rented_books:
            user = rental.user
            book_title = rental.book 
            message_text = f'Hello {user.name}, your rented book Title: {book_title} is due soon. Please return it by {rental.return_date}.'     
            # Save notification to the Notification model
            notification = Notification(user=user, message=message_text)
            notification.save()
