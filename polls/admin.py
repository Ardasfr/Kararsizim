from django.contrib import admin
from .models import Poll, Choice, Vote, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('icon', 'name', 'slug', 'order')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2
    min_num = 2
    max_num = 5

@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ('question', 'author', 'category', 'is_active', 'created_at', 'expires_at', 'total_votes')
    list_editable = ('is_active',)
    list_filter = ('is_active', 'category', 'created_at')
    search_fields = ('question', 'author__username')
    inlines = [ChoiceInline]
    actions = ['deactivate_polls', 'activate_polls']

    @admin.action(description='⚠️ Seçilen anketleri yayından kaldır (Pasife Al)')
    def deactivate_polls(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} adet anket başarıyla yayından kaldırıldı.')

    @admin.action(description='✅ Seçilen anketleri yeniden yayına al')
    def activate_polls(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} adet anket yeniden yayına alındı.')

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('poll', 'choice', 'user', 'session_key', 'ip_address', 'voted_at')
    list_filter = ('voted_at',)
    search_fields = ('poll__question', 'user__username', 'session_key')
