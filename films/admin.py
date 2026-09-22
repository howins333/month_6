from django.contrib import admin

# Register your models here.
from .models import Film, Director, Genre, Review

admin.site.register(Film)
admin.site.register(Director)
admin.site.register(Genre)
admin.site.register(Review)
