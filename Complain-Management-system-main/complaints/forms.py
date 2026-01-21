from django import forms
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from .models import (
    UserProfile,
    Complaint, Feedback
)
from .models import UserProfile as ProfileModel


class UserRegisterForm(forms.Form):
    """User registration form with enhanced validators"""
    USER_TYPE_CHOICES = [
        ('student', 'Student'),
        ('faculty', 'Faculty'),
    ]
    CATEGORY_CHOICES = [('', 'Select Category')] + list(ProfileModel.CATEGORY_CHOICES)
    
    # Phone validator: exactly 10 digits
    phone_validator = RegexValidator(
        regex=r'^\d{10}$',
        message='Phone number must be exactly 10 digits.'
    )
    
    username = forms.CharField(
        label="Full Name", 
        max_length=150,
        min_length=3,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm',
            'placeholder': 'Enter your full name',
            'id': 'id_username'
        }),
        help_text='Minimum 3 characters required'
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm',
            'placeholder': 'Enter your email address',
            'id': 'id_email',
            'type': 'email'
        }),
        help_text='A valid email address is required'
    )
    
    user_id = forms.CharField(
        label="Student/Faculty ID", 
        max_length=20,
        min_length=3,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm',
            'placeholder': 'Enter your ID',
            'id': 'id_user_id'
        })
    )
    
    department = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm',
            'placeholder': 'Enter your department',
            'id': 'id_department'
        })
    )
    
    phone = forms.CharField(
        max_length=15,
        required=True,
        validators=[phone_validator],
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm',
            'placeholder': 'Enter 10-digit phone number',
            'id': 'id_phone',
            'pattern': '[0-9]{10}',
            'maxlength': '10'
        }),
        help_text='Must be exactly 10 digits (e.g., 9876543210)'
    )
    
    age = forms.IntegerField(
        required=True,
        min_value=15,
        max_value=120,
        widget=forms.NumberInput(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm',
            'placeholder': 'Enter your age',
            'id': 'id_age',
            'min': '15',
            'max': '120'
        }),
        help_text='Minimum age is 15 years'
    )
    
    password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 pr-12 rounded-xl glass border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#4dd0e1]',
            'placeholder': 'Enter password (min 8 characters)',
            'id': 'id_password'
        }),
        help_text='Password must be at least 8 characters long'
    )
    
    password_confirm = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 pr-12 rounded-xl glass border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#4dd0e1]',
            'placeholder': 'Confirm your password',
            'id': 'id_password_confirm'
        })
    )
    
    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm',
            'id': 'user_type'
        })
    )
    category = forms.ChoiceField(
        required=False,
        choices=CATEGORY_CHOICES,
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm',
            'id': 'id_category'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords don't match")
        
        # Password strength validation
        if password:
            if len(password) < 8:
                raise forms.ValidationError("Password must be at least 8 characters long")
            if not any(char.isdigit() for char in password):
                raise forms.ValidationError("Password must contain at least one number")
            if not any(char.isalpha() for char in password):
                raise forms.ValidationError("Password must contain at least one letter")
        
        return cleaned_data
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise forms.ValidationError("Full name is required")
        if len(username) < 3:
            raise forms.ValidationError("Full name must be at least 3 characters long")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("A user with this username already exists")
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("Email is required")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists")
        # Additional email format validation
        if '@' not in email or '.' not in email.split('@')[1]:
            raise forms.ValidationError("Please enter a valid email address")
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone:
            raise forms.ValidationError("Phone number is required")
        # Remove any non-digit characters
        phone = ''.join(filter(str.isdigit, phone))
        if len(phone) != 10:
            raise forms.ValidationError("Phone number must be exactly 10 digits")
        return phone
    
    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age is None:
            raise forms.ValidationError("Age is required")
        if age < 15:
            raise forms.ValidationError("You must be at least 15 years old to register")
        if age > 120:
            raise forms.ValidationError("Please enter a valid age")
        return age
    
    def clean_user_type(self):
        """Prevent HOD registration through form"""
        user_type = self.cleaned_data.get('user_type')
        if user_type == 'hod':
            raise forms.ValidationError("HOD accounts can only be created by administrators.")
        return user_type


class ComplaintForm(forms.ModelForm):
    """Complaint creation/editing form"""
    
    class Meta:
        model = Complaint
        fields = [
            'title', 'description', 'category','subcategory',
            'attachment'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl glass border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#4dd0e1] transition-all',
                'placeholder': 'Enter complaint title'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-xl glass border border-white/10 text-white focus:outline-none focus:ring-2 focus:ring-[#4dd0e1] transition-all bg-[#0d0f18]'
            }),
            'subcategory': forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-xl glass border border-white/10 text-white focus:outline-none focus:ring-2 focus:ring-[#4dd0e1] transition-all bg-[#0d0f18]'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-xl glass border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#4dd0e1] transition-all',
                'rows': 5,
                'placeholder': 'Describe your complaint in detail'
            }),
            'attachment': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl glass border border-white/10 text-white file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-semibold file:bg-[#4dd0e1]/20 file:text-[#4dd0e1] hover:file:bg-[#4dd0e1]/30 cursor-pointer',
                'accept': '.pdf,.jpg,.jpeg,.png,.docx'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields optional
        self.fields['attachment'].required = False
    
    def clean_attachment(self):
        attachment = self.cleaned_data.get('attachment')
        if attachment:
            # Check file size (10MB limit)
            if attachment.size > 10 * 1024 * 1024:
                raise forms.ValidationError("File size cannot exceed 10MB")
            
            # Check file extension
            allowed_extensions = ['pdf', 'jpg', 'jpeg', 'png', 'docx']
            file_extension = attachment.name.split('.')[-1].lower()
            if file_extension not in allowed_extensions:
                raise forms.ValidationError(
                    f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
                )
        
        return attachment


class ComplaintUpdateForm(forms.ModelForm):
    """Complaint update form for faculty/admin"""
    
    class Meta:
        model = Complaint
        fields = ['status', 'remarks', 'admin_remarks']
    widgets = {
        'remarks': forms.Textarea(attrs={
            'class': 'form-control dark-textarea',
            'rows': 3,
            'placeholder': 'Update remarks'
        }),
        'admin_remarks': forms.Textarea(attrs={
            'class': 'form-control dark-textarea',
            'rows': 3,
            'placeholder': 'Admin remarks'
        }),
    }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Hide admin_remarks for non-admin users
        if not user or not user.is_staff:
            self.fields.pop('admin_remarks', None)


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['comments']
        widgets = {
            'comments': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-xl glass bg-[#0d0f18] text-white placeholder-gray-400 border border-white/10 focus:outline-none focus:ring-2 focus:ring-[#4dd0e1]',
                'rows': 4,
                'placeholder': 'Share your experience with the complaint resolution'
            }),
        }


class ComplaintAssignmentForm(forms.Form):
    """Complaint assignment form"""
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Only show HOD in assignment if user is superuser
        if user and user.is_superuser:
            queryset = User.objects.filter(profile__role__in=['faculty', 'hod'])
            empty_label = "Select Faculty Member or HOD"
        else:
            queryset = User.objects.filter(profile__role='faculty')
            empty_label = "Select Faculty Member"
        
        self.fields['assigned_to'] = forms.ModelChoiceField(
            queryset=queryset,
            empty_label=empty_label,
            widget=forms.Select(attrs={
                'class': 'form-control dark-select'
            })
            )

    remarks = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control dark-textarea',
            'rows': 3,
            'placeholder': 'Assignment remarks (optional)'
        })
    )





class ComplaintFilterForm(forms.Form):
    """Complaint filtering form"""
    STATUS_CHOICES = [('', 'All Statuses')] + list(Complaint.STATUS_CHOICES)
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search complaints...'
        })
    )


class ProfileUpdateForm(forms.ModelForm):
    """User profile update form"""
    
    class Meta:
        model = UserProfile
        fields = ['phone', 'department', 'category']
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter department'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Prevent non-superusers from changing role to HOD
        if user and not user.is_superuser:
            # Remove role field if it exists
            if 'role' in self.fields:
                del self.fields['role']


class UserUpdateForm(forms.ModelForm):
    """User account update form"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter last name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email address'
            }),
        }

class StudentComplaintEditForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['description', 'attachment']
        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-xl glass border border-white/10 text-white',
                'rows': 5
            }),
            'attachment': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl glass border border-white/10 text-white'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['attachment'].required = False
