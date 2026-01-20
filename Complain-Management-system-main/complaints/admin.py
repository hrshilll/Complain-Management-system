from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import (
    UserProfile,
    Complaint,
    ComplaintHistory,
    Feedback,
    Notification
)


# =========================
# User Profile Inline
# =========================
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('role', 'phone', 'department', 'category')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Only superusers can assign HOD role
        if not request.user.is_superuser and 'role' in form.base_fields:
            form.base_fields['role'].choices = [
                choice for choice in form.base_fields['role'].choices
                if choice[0] != 'hod'
            ]
        return form


# =========================
# Custom User Admin
# =========================
class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'get_role', 'is_staff', 'date_joined'
    )
    list_filter = (
        'is_staff', 'is_superuser', 'is_active',
        'date_joined', 'profile__role'
    )
    search_fields = ('username', 'first_name', 'last_name', 'email')

    def get_role(self, obj):
        try:
            return obj.profile.get_role_display()
        except Exception:
            return 'No Profile'

    get_role.short_description = 'Role'


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# =========================
# UserProfile Admin
# =========================
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'category', 'phone', 'department')
    list_filter = ('role', 'category', 'department')
    search_fields = (
        'user__username',
        'user__first_name',
        'user__last_name',
        'phone',
        'department',
        'category'
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser and 'role' in form.base_fields:
            form.base_fields['role'].choices = [
                choice for choice in form.base_fields['role'].choices
                if choice[0] != 'hod'
            ]
        return form


# =========================
# Complaint History Inline
# =========================
class ComplaintHistoryInline(admin.TabularInline):
    model = ComplaintHistory
    extra = 0
    readonly_fields = ('changed_by', 'from_status', 'to_status', 'timestamp')
    fields = ('changed_by', 'from_status', 'to_status', 'remarks', 'timestamp')


# =========================
# Complaint Admin
# =========================
@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = (
        'complaint_no',
        'title',
        'category',
        'priority',
        'user',
        'assigned_to',
        'status',
        'created_at',
        'resolved_at'
    )
    list_filter = (
        'status',
        'priority',
        'category',
        'assigned_to',
        'created_at'
    )
    search_fields = (
        'complaint_no',
        'title',
        'description',
        'user__username',
        'assigned_to__username'
    )
    readonly_fields = ('complaint_no', 'created_at', 'resolved_at')
    inlines = [ComplaintHistoryInline]
    ordering = ('-created_at',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('complaint_no', 'title', 'description', 'category', 'subcategory', 'user')
        }),
        ('Assignment & Status', {
            'fields': ('assigned_to', 'status', 'priority', 'resolved_at')
        }),
        ('Attachments & Remarks', {
            'fields': ('attachment', 'remarks', 'admin_remarks')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'assigned_to')


# =========================
# Complaint History Admin
# =========================
@admin.register(ComplaintHistory)
class ComplaintHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'complaint',
        'changed_by',
        'from_status',
        'to_status',
        'timestamp'
    )
    list_filter = ('from_status', 'to_status', 'timestamp')
    search_fields = (
        'complaint__complaint_no',
        'complaint__title',
        'changed_by__username'
    )
    readonly_fields = ('timestamp',)


# =========================
# Feedback Admin
# =========================
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'user', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('complaint__complaint_no', 'user__username')
    readonly_fields = ('created_at',)


# =========================
# Notification Admin
# =========================
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message_preview', 'is_read', 'created_at')
    list_filter = ('is_read',)
    search_fields = ('user__username', 'message')
    readonly_fields = ('created_at',)

    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message

    message_preview.short_description = 'Message'
from .models import Category, SubCategory, Complaint

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'faculty')

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'faculty', 'priority')
    list_filter = ('category', 'priority')



# =========================
# Admin Branding
# =========================
admin.site.site_header = "Complaint Management System"
admin.site.site_title = "CMS Admin"
admin.site.index_title = "Welcome to Complaint Management System"
