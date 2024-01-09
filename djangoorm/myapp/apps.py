from django.apps import AppConfig


class MyappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "myapp"
    

# i want to schedule a cron job using cron.py file so that if some users rented a specific book then we have to send the notifications on each day that you have some days left to return our book
# this is  will be checking of user authentication and then send each logged in user 

