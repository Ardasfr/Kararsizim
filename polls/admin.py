from django.contrib import admin
from .models import Poll, Choice, Vote

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2
    min_num = 2
    max_num = 5

@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ('question', 'author', 'created_at', 'total_votes', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('question', 'author__username')
    inlines = [ChoiceInline]

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('poll', 'choice', 'user', 'session_key', 'ip_address', 'voted_at')
    list_filter = ('voted_at',)
    search_fields = ('poll__question', 'user__username', 'session_key')
