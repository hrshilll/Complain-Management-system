import uuid
import os
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Max


# =========================
# File upload helper
# =========================
def upload_to(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('complaints', filename)


# =========================
# User Profile
# =========================
class UserProfile(models.Model):

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
    phone = models.CharField(max_length=15, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


# =========================
# Complaint
# =========================



def upload_to(instance, filename):
    return f"complaints/{instance.user.username}/{filename}"

from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    faculty = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        limit_choices_to={'profile__role': 'faculty'}
    )

    def __str__(self):
        return self.name

class SubCategory(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='subcategories'
    )
    name = models.CharField(max_length=100)

    # Optional override faculty
    faculty = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        limit_choices_to={'profile__role': 'faculty'}
    )

    # ✅ PRIORITY PER SUBCATEGORY
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Critical', 'Critical'),
    ]
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='Low'
    )

    def __str__(self):
        return f"{self.name}"

class Complaint(models.Model):

    # ==========================
    # STATUS
    # ==========================
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('RESOLVED', 'Resolved'),
        ('REJECTED', 'Rejected'),
    ]

    # ==========================
    # BASIC INFO
    # ==========================
    complaint_no = models.CharField(
        max_length=20,
        unique=True,
        blank=True
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='complaints'
    )

    title = models.CharField(max_length=200)
    description = models.TextField()

    attachment = models.FileField(
        upload_to=upload_to,
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png', 'docx'])
        ]
    )

    # ==========================
    # CATEGORY STRUCTURE
    # ==========================
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='complaints'
    )

    subcategory = models.ForeignKey(
        SubCategory,
        on_delete=models.CASCADE,
        related_name='complaints'
    )

    # ==========================
    # SYSTEM GENERATED
    # ==========================
    priority = models.CharField(
        max_length=10,
        choices=SubCategory.PRIORITY_CHOICES,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_complaints'
    )

    remarks = models.TextField(blank=True)
    admin_remarks = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    # ==========================
    # STRING
    # ==========================
    def __str__(self):
        return f"{self.complaint_no} - {self.title}"
    
    

        # ==========================
        # SAVE LOGIC
        # ==========================
    def save(self, *args, **kwargs):
        if not self.pk and not self.complaint_no:
            self.complaint_no = self.generate_complaint_no()
        super().save(*args, **kwargs)



    # ==========================
    # COMPLAINT NUMBER
    # ==========================

    def generate_complaint_no(self):
        today = timezone.now().strftime('%Y%m%d')
        last = Complaint.objects.filter(
            complaint_no__startswith=f"CMP-{today}"
        ).aggregate(Max('complaint_no'))['complaint_no__max']

        if last:
            last_number = int(last.split('-')[-1])
            next_number = last_number + 1
        else:
            next_number = 1

        return f"CMP-{today}-{next_number:04d}"



# =========================
# Complaint History
# =========================
class ComplaintHistory(models.Model):

    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='history')
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    from_status = models.CharField(max_length=20)
    to_status = models.CharField(max_length=20)
    remarks = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.complaint.complaint_no}: {self.from_status} → {self.to_status}"


# =========================
# Feedback
# =========================
class Feedback(models.Model):

    complaint = models.OneToOneField(Complaint, on_delete=models.CASCADE, related_name='feedback')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comments = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback - {self.complaint.complaint_no}"


# =========================
# Notification
# =========================
class Notification(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}"




