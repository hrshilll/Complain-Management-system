import uuid
import os
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.db.models import Count, Q


def upload_to(instance, filename):
    """Generate unique filename for uploads"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('complaints', filename)


class UserProfile(models.Model):
    """Extended user profile with role and additional fields"""
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('hod', 'HOD'),
        ('admin', 'Admin'),
    ]
    CATEGORY_CHOICES = [
        ('academic', 'Academic Issues'),
        ('disciplinary', 'Disciplinary / Conduct Issues'),
        ('hostel', 'Hostel / Accommodation Issues'),
        ('mess', 'Mess / Food Quality'),
        ('transport', 'Transport / Bus Facility'),
        ('library', 'Library & Study Resources'),
        ('lab', 'Lab / Equipment Issues'),
        ('maintenance', 'Campus Maintenance'),
        ('it', 'IT / Internet / Login Issues'),
        ('administration', 'Administrative / Documentation'),
        ('finance', 'Fees / Accounts / Scholarship'),
        ('security', 'Safety / Security'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    phone = models.CharField(max_length=15, null=True, blank=True)
    department = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, blank=True)
    age = models.IntegerField(null=True, blank=True, help_text='Age must be at least 15')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"


class Complaint(models.Model):
    """Main complaint model"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('RESOLVED', 'Resolved'),
        ('COMPLETED', 'Completed'),
        ('REJECTED', 'Rejected'),
    ]
    CATEGORY_CHOICES = UserProfile.CATEGORY_CHOICES

    complaint_no = models.CharField(max_length=20, unique=True, db_index=True, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    attachment = models.FileField(
        upload_to=upload_to,
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png', 'docx'])],
        help_text="Maximum file size: 10MB. Allowed formats: PDF, JPG, PNG, DOCX"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints', null=True, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, db_index=True, default='administration')
    assigned_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_complaints',
        limit_choices_to={'profile__role__in': ['faculty', 'hod']}
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(blank=True)
    admin_remarks = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['complaint_no']),
            models.Index(fields=['status']),
            models.Index(fields=['user']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['category']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.complaint_no} - {self.title}"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('complaint_detail', kwargs={'complaint_no': self.complaint_no})
    
    def clean(self):
        """Validate file size"""
        if self.attachment:
            if self.attachment.size > 10 * 1024 * 1024:  # 10MB
                raise ValidationError('File size cannot exceed 10MB')
    
    def save(self, *args, **kwargs):
        if not self.complaint_no:
            self.complaint_no = self.generate_complaint_no()
        
        # Set resolved_at when status changes to RESOLVED
        if self.status == 'RESOLVED' and not self.resolved_at:
            self.resolved_at = timezone.now()
        
        # Auto-assign based on category if not already assigned
        if not self.assigned_to and self.category:
            # Determine if complaint is from faculty or student
            user_role = None
            user_department = None
            if self.user and hasattr(self.user, 'profile'):
                user_role = self.user.profile.role
                user_department = self.user.profile.department
            
            # If complaint is from faculty, assign to HOD
            if user_role == 'faculty':
                # First try: Find HOD with matching department (preferred)
                if user_department:
                    matching_hod = User.objects.filter(
                        profile__role='hod',
                        profile__department=user_department
                    ).annotate(
                        open_count=Count(
                            'assigned_complaints',
                            filter=Q(assigned_complaints__status__in=['PENDING', 'PROCESSING'])
                        )
                    ).order_by('open_count', 'date_joined').first()
                    
                    if matching_hod:
                        self.assigned_to = matching_hod
                
                # Second try: Find HOD with matching category if department match failed
                if not self.assigned_to:
                    matching_hod = User.objects.filter(
                        profile__role='hod',
                        profile__category=self.category
                    ).annotate(
                        open_count=Count(
                            'assigned_complaints',
                            filter=Q(assigned_complaints__status__in=['PENDING', 'PROCESSING'])
                        )
                    ).order_by('open_count', 'date_joined').first()
                    
                    if matching_hod:
                        self.assigned_to = matching_hod
                
                # Fallback: any HOD
                if not self.assigned_to:
                    fallback_hod = User.objects.filter(profile__role='hod').annotate(
                        open_count=Count(
                            'assigned_complaints',
                            filter=Q(assigned_complaints__status__in=['PENDING', 'PROCESSING'])
                        )
                    ).order_by('open_count', 'date_joined').first()
                    if fallback_hod:
                        self.assigned_to = fallback_hod
            
            # If complaint is from student, assign to faculty with matching category
            elif user_role == 'student':
                # Find faculty with matching category and fewest open complaints
                matching_faculty = User.objects.filter(
                    profile__role='faculty',
                    profile__category=self.category
                ).annotate(
                    open_count=Count(
                        'assigned_complaints',
                        filter=Q(assigned_complaints__status__in=['PENDING', 'PROCESSING'])
                    )
                ).order_by('open_count', 'date_joined').first()
                
                if matching_faculty:
                    self.assigned_to = matching_faculty
                else:
                    # Fallback: any faculty member (if no category match)
                    fallback_faculty = User.objects.filter(profile__role='faculty').annotate(
                        open_count=Count(
                            'assigned_complaints',
                            filter=Q(assigned_complaints__status__in=['PENDING', 'PROCESSING'])
                        )
                    ).order_by('open_count', 'date_joined').first()
                    if fallback_faculty:
                        self.assigned_to = fallback_faculty
                    else:
                        # Last fallback: any admin/staff user
                        fallback_user = User.objects.filter(
                            Q(is_staff=True) | Q(profile__role='admin')
                        ).order_by('date_joined').first()
                        if fallback_user:
                            self.assigned_to = fallback_user
        
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_complaint_no():
        """Generate unique complaint number: CMP-YYYYMMDD-XXXXXX"""
        today = timezone.now().date()
        date_str = today.strftime('%Y%m%d')
        
        # Get the last complaint number for today
        last_complaint = Complaint.objects.filter(
            complaint_no__startswith=f'CMP-{date_str}'
        ).order_by('-complaint_no').first()
        
        if last_complaint:
            # Extract the sequence number and increment
            last_seq = int(last_complaint.complaint_no.split('-')[-1])
            next_seq = last_seq + 1
        else:
            next_seq = 1
        
        return f'CMP-{date_str}-{next_seq:06d}'


class ComplaintHistory(models.Model):
    """Audit trail for complaint changes"""
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='history')
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    from_status = models.CharField(max_length=20, blank=True)
    to_status = models.CharField(max_length=20, blank=True)
    remarks = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Complaint Histories'
    
    def __str__(self):
        return f"{self.complaint.complaint_no} - {self.from_status} → {self.to_status}"


class Feedback(models.Model):
    """User feedback for resolved complaints"""
    complaint = models.OneToOneField(Complaint, on_delete=models.CASCADE, related_name='feedback')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comments = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Feedback for {self.complaint.complaint_no} - {self.rating}/5"


class Notification(models.Model):
    """In-app notifications"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification for {self.user.username} - {self.message[:50]}..."


# Signals for automatic history creation
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver


@receiver(pre_save, sender=Complaint)
def track_complaint_changes(sender, instance, **kwargs):
    """Track changes to complaint status and assignment"""
    if instance.pk:
        try:
            old_instance = Complaint.objects.get(pk=instance.pk)
            if old_instance.status != instance.status or old_instance.assigned_to != instance.assigned_to:
                # Create history entry
                ComplaintHistory.objects.create(
                    complaint=instance,
                    changed_by=instance.user,  # This will be updated by the view
                    from_status=old_instance.status,
                    to_status=instance.status,
                    remarks=f"Status changed from {old_instance.status} to {instance.status}"
                )
        except Complaint.DoesNotExist:
            pass

