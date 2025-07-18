from django.contrib import admin

# Register your models here.


from .models import User, State, District   
admin.site.register(User)
admin.site.register(State)
admin.site.register(District)