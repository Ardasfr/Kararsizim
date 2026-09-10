from django.contrib import admin
from .models import Wheel, WheelOption

class WheelOptionInline(admin.TabularInline):
    model = WheelOption
    extra = 2

@admin.register(Wheel)
class WheelAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_public', 'spin_count', 'options_count', 'created_at')
    list_filter = ('is_public', 'created_at')
    search_fields = ('title', 'description', 'author__username')
    inlines = [WheelOptionInline]
