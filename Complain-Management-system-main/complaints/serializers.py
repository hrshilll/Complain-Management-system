from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    UserProfile,
    Complaint, ComplaintHistory, Feedback, Notification
)


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profiles"""
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'phone', 'department', 'category', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_role(self, value):
        """Prevent non-superusers from setting role to HOD"""
        request = self.context.get('request')
        if value == 'hod' and (not request or not request.user.is_superuser):
            raise serializers.ValidationError("Only superusers can set role to HOD.")
        return value


class ComplaintListSerializer(serializers.ModelSerializer):
    """Serializer for complaint list view"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    attachment_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Complaint
        fields = [
            'complaint_no', 'title', 'description', 'category', 'status',
            'user_name', 'user_username', 'assigned_to_name',
            'attachment_url', 'created_at', 'updated_at', 'resolved_at'
        ]
        read_only_fields = ['complaint_no', 'created_at', 'updated_at', 'resolved_at']
    
    def get_attachment_url(self, obj):
        if obj.attachment:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.attachment.url)
        return None


class ComplaintDetailSerializer(serializers.ModelSerializer):
    """Serializer for complaint detail view"""
    user_profile = UserProfileSerializer(source='user.profile', read_only=True)
    assigned_to_profile = UserProfileSerializer(source='assigned_to.profile', read_only=True)
    attachment_url = serializers.SerializerMethodField()
    history = serializers.SerializerMethodField()
    feedback = serializers.SerializerMethodField()
    
    class Meta:
        model = Complaint
        fields = [
            'complaint_no', 'title', 'description', 'category', 'status',
            'user_profile', 'assigned_to_profile',
            'attachment_url', 'remarks', 'admin_remarks', 'history', 'feedback',
            'created_at', 'updated_at', 'resolved_at'
        ]
        read_only_fields = ['complaint_no', 'created_at', 'updated_at', 'resolved_at']
    
    def get_attachment_url(self, obj):
        if obj.attachment:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.attachment.url)
        return None
    
    def get_history(self, obj):
        history = obj.history.all()[:10]  # Last 10 entries
        return ComplaintHistorySerializer(history, many=True, context=self.context).data
    
    def get_feedback(self, obj):
        try:
            feedback = obj.feedback
            return FeedbackSerializer(feedback, context=self.context).data
        except Feedback.DoesNotExist:
            return None


class ComplaintCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating complaints"""
    
    class Meta:
        model = Complaint
        fields = [
            'title', 'description', 'category',
            'attachment', 'remarks'
        ]
    
    def validate_attachment(self, value):
        """Validate file upload"""
        if value:
            # Check file size (10MB limit)
            if value.size > 10 * 1024 * 1024:
                raise serializers.ValidationError("File size cannot exceed 10MB")
            
            # Check file extension
            allowed_extensions = ['pdf', 'jpg', 'jpeg', 'png', 'docx']
            file_extension = value.name.split('.')[-1].lower()
            if file_extension not in allowed_extensions:
                raise serializers.ValidationError(
                    f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
                )
        
        return value


class ComplaintUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating complaints"""
    
    class Meta:
        model = Complaint
        fields = ['status', 'remarks', 'admin_remarks']
    
    def validate_status(self, value):
        """Validate status transitions"""
        if self.instance:
            current_status = self.instance.status
            user = self.context['request'].user
            
            # Only admin can close complaints
            if value == 'CLOSED' and not user.is_staff:
                raise serializers.ValidationError("Only administrators can close complaints")
            
            # Only assigned faculty or admin can change status
            if (current_status != value and 
                user != self.instance.assigned_to and 
                not user.is_staff):
                raise serializers.ValidationError("Only assigned faculty or admin can change status")
        
        return value


class ComplaintAssignmentSerializer(serializers.Serializer):
    """Serializer for assigning complaints"""
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(profile__role__in=['faculty', 'hod']),
        required=True
    )
    remarks = serializers.CharField(required=False, allow_blank=True)
    
    def validate_assigned_to(self, value):
        """Validate assignment - only superusers can assign to HOD"""
        request = self.context.get('request')
        if not hasattr(value, 'profile'):
            raise serializers.ValidationError("Selected user does not have a profile.")
        
        if value.profile.role == 'hod' and (not request or not request.user.is_superuser):
            raise serializers.ValidationError("Only superusers can assign complaints to HOD.")
        
        if value.profile.role not in ['faculty', 'hod']:
            raise serializers.ValidationError("Can only assign to faculty members or HOD.")
        return value


class ComplaintHistorySerializer(serializers.ModelSerializer):
    """Serializer for complaint history"""
    changed_by_name = serializers.CharField(source='changed_by.get_full_name', read_only=True)
    
    class Meta:
        model = ComplaintHistory
        fields = [
            'id', 'changed_by_name', 'from_status', 'to_status',
            'remarks', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


class FeedbackSerializer(serializers.ModelSerializer):
    """Serializer for feedback"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    complaint_no = serializers.CharField(source='complaint.complaint_no', read_only=True)
    
    class Meta:
        model = Feedback
        fields = [
            'id', 'complaint_no', 'rating', 'comments', 'user_name', 'created_at'
        ]
        read_only_fields = ['id', 'user_name', 'complaint_no', 'created_at']
    
    def validate_rating(self, value):
        """Validate rating"""
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications"""
    
    class Meta:
        model = Notification
        fields = ['id', 'message', 'is_read', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for users"""
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_active', 'date_joined', 'profile'
        ]
        read_only_fields = ['id', 'date_joined']


class ComplaintStatsSerializer(serializers.Serializer):
    """Serializer for complaint statistics"""
    total_complaints = serializers.IntegerField()
    pending_complaints = serializers.IntegerField()
    in_progress_complaints = serializers.IntegerField()
    resolved_complaints = serializers.IntegerField()
    closed_complaints = serializers.IntegerField()
    avg_resolution_time = serializers.DurationField(allow_null=True)
    complaints_by_month = serializers.DictField()
