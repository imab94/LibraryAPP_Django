from django.contrib import admin
from .models import Author,Reader,Book,Carousals,CustomUser,Rating,Comment,Rental,Notification

# Register your models here.

admin.site.register(Author)
admin.site.register(Reader)
admin.site.register(Carousals)

class CustomUserAdmin(admin.ModelAdmin):
    readonly_fields = ('password',)
    

class RatingAdmin(admin.ModelAdmin):
    list_display = ('id','user','book','rating')


class BookAdmin(admin.ModelAdmin):
    list_filter = ('title','rating','author')
    

class RentalAdmin(admin.ModelAdmin):
    list_display = ('user','book','rented_date','return_date','returned')
    list_filter = ('user','rented_date','returned')
        
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user','message','created_at','day_left')
    list_filter = ('user','message','created_at','day_left')
    
    
admin.site.register(CustomUser,CustomUserAdmin)
admin.site.register(Rating,RatingAdmin)
admin.site.register(Book,BookAdmin)
admin.site.register(Comment)
admin.site.register(Rental,RentalAdmin)
admin.site.register(Notification,NotificationAdmin)
