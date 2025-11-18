from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import (
    UserProfile,
    Complaint, ComplaintHistory, Feedback, Notification
)


class UserProfileInline(admin.StackedInline):
    """Inline admin for user profiles"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('role', 'phone', 'department', 'category')
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Only superusers can set role to HOD
        if not request.user.is_superuser:
            form.base_fields['role'].choices = [
                choice for choice in form.base_fields['role'].choices 
                if choice[0] != 'hod'
            ]
        return form


class CustomUserAdmin(UserAdmin):
    """Custom user admin with profile inline"""
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined', 'profile__role')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    
    def get_role(self, obj):
        """Get user role from profile"""
        try:
            return obj.profile.get_role_display()
        except:
            return 'No Profile'
    get_role.short_description = 'Role'


# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin for user profiles"""
    list_display = ('user', 'role', 'category', 'phone', 'department', 'created_at')
    list_filter = ('role', 'category', 'department', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone', 'department', 'category')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Only superusers can set role to HOD
        if not request.user.is_superuser:
            if 'role' in form.base_fields:
                form.base_fields['role'].choices = [
                    choice for choice in form.base_fields['role'].choices 
                    if choice[0] != 'hod'
                ]
        return form
    
    def save_model(self, request, obj, form, change):
        # Prevent non-superusers from creating/updating HOD profiles
        if obj.role == 'hod' and not request.user.is_superuser:
            from django.contrib import messages
            messages.error(request, "Only superusers can create or modify HOD accounts.")
            return
        super().save_model(request, obj, form, change)


class ComplaintHistoryInline(admin.TabularInline):
    """Inline admin for complaint history"""
    model = ComplaintHistory
    extra = 0
    readonly_fields = ('changed_by', 'from_status', 'to_status', 'timestamp')
    fields = ('changed_by', 'from_status', 'to_status', 'remarks', 'timestamp')


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    """Admin for complaints"""
    list_display = (
        'complaint_no', 'title', 'category', 'user', 'assigned_to', 'status',
        'created_at', 'resolved_at'
    )
    list_filter = (
        'status', 'assigned_to', 'category',
        'created_at', 'resolved_at'
    )
    search_fields = (
        'complaint_no', 'title', 'description', 'user__username',
        'assigned_to__username'
    )
    readonly_fields = ('complaint_no', 'created_at', 'updated_at', 'resolved_at')
    inlines = [ComplaintHistoryInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('complaint_no', 'title', 'description', 'category', 'user')
        }),
        ('Assignment & Status', {
            'fields': ('assigned_to', 'status', 'resolved_at')
        }),
        ('Attachments & Remarks', {
            'fields': ('attachment', 'remarks', 'admin_remarks')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related(
            'user', 'assigned_to'
        )


@admin.register(ComplaintHistory)
class ComplaintHistoryAdmin(admin.ModelAdmin):
    """Admin for complaint history"""
    list_display = ('complaint', 'changed_by', 'from_status', 'to_status', 'timestamp')
    list_filter = ('from_status', 'to_status', 'timestamp')
    search_fields = ('complaint__complaint_no', 'complaint__title', 'changed_by__username')
    readonly_fields = ('timestamp',)


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    """Admin for feedback"""
    list_display = ('complaint', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('complaint__complaint_no', 'user__username', 'comments')
    readonly_fields = ('created_at',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin for notifications"""
    list_display = ('user', 'message_preview', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'message')
    readonly_fields = ('created_at',)
    
    def message_preview(self, obj):
        """Show message preview"""
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message'


# Customize admin site
admin.site.site_header = "Complaint Management System"
admin.site.site_title = "CMS Admin"
admin.site.index_title = "Welcome to Complaint Management System"