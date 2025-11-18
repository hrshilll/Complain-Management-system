
import logging
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib.auth import login, logout
from django.contrib import messages
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.urls import reverse
from django.http import Http404

# REST Framework imports
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authtoken.models import Token
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

# Local imports
from .models import (
    UserProfile,
    Complaint, ComplaintHistory, Feedback, Notification
)
from .forms import UserRegisterForm, ComplaintForm, FeedbackForm
from .serializers import (
    UserProfileSerializer,
    ComplaintListSerializer, ComplaintDetailSerializer,
    ComplaintCreateSerializer, ComplaintUpdateSerializer, ComplaintAssignmentSerializer,
    ComplaintHistorySerializer, FeedbackSerializer, NotificationSerializer,
    UserSerializer, ComplaintStatsSerializer
)

logger = logging.getLogger(__name__)


# Template Views
@login_required
def dashboard(request):
    """Role-aware dashboard"""
    user_profile = getattr(request.user, 'profile', None)
    
    if not user_profile:
        messages.error(request, "User profile not found. Please contact administrator.")
        return redirect('logout')
    
    role = user_profile.role
    
    # Get complaint statistics based on role
    if role == 'admin':
        complaints = Complaint.objects.all()
        stats = {
            'total': complaints.count(),
            'pending': complaints.filter(status='PENDING').count(),
            'in_progress': complaints.filter(status='IN_PROGRESS').count(),
            'resolved': complaints.filter(status='RESOLVED').count(),
            'closed': complaints.filter(status='CLOSED').count(),
        }
        recent_complaints = complaints.order_by('-created_at')[:10]
        
    elif role == 'hod':
        # HOD sees complaints assigned to them (from faculty)
        complaints = Complaint.objects.filter(assigned_to=request.user)
        stats = {
            'total': complaints.count(),
            'pending': complaints.filter(status='PENDING').count(),
            'in_progress': complaints.filter(status='IN_PROGRESS').count(),
            'resolved': complaints.filter(status='RESOLVED').count(),
            'closed': complaints.filter(status='CLOSED').count(),
        }
        recent_complaints = complaints.order_by('-created_at')[:10]
        
    elif role == 'faculty':
        # Faculty sees complaints assigned to them (from students) AND complaints they created (assigned to HOD)
        complaints = Complaint.objects.filter(
            Q(assigned_to=request.user) | Q(user=request.user)
        )
        stats = {
            'total': complaints.count(),
            'pending': complaints.filter(status='PENDING').count(),
            'in_progress': complaints.filter(status='IN_PROGRESS').count(),
            'resolved': complaints.filter(status='RESOLVED').count(),
            'closed': complaints.filter(status='CLOSED').count(),
        }
        recent_complaints = complaints.order_by('-created_at')[:10]
        
    else:  # student
        complaints = Complaint.objects.filter(user=request.user)
        stats = {
            'total': complaints.count(),
            'pending': complaints.filter(status='PENDING').count(),
            'in_progress': complaints.filter(status='IN_PROGRESS').count(),
            'resolved': complaints.filter(status='RESOLVED').count(),
            'closed': complaints.filter(status='CLOSED').count(),
        }
        recent_complaints = complaints.order_by('-created_at')[:10]
    
    # Get notifications
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:5]
    
    context = {
        'role': role,
        'stats': stats,
        'recent_complaints': recent_complaints,
        'notifications': notifications,
    }
    
    return render(request, 'complaints/dashboard.html', context)


@login_required
def complaint_list(request):
    """List complaints with filtering"""
    user_profile = getattr(request.user, 'profile', None)
    role = user_profile.role if user_profile else 'student'
    
    # Base queryset based on role
    if role == 'admin':
        complaints = Complaint.objects.all()
    elif role == 'hod':
        # HOD sees complaints assigned to them (from faculty)
        complaints = Complaint.objects.filter(assigned_to=request.user)
    elif role == 'faculty':
        # Faculty sees complaints assigned to them (from students) AND complaints they created (assigned to HOD)
        complaints = Complaint.objects.filter(
            Q(assigned_to=request.user) | Q(user=request.user)
        )
    else:  # student
        complaints = Complaint.objects.filter(user=request.user)
    
    # Apply filters
    status_filter = request.GET.get('status')
    search_query = request.GET.get('search')
    
    if status_filter:
        complaints = complaints.filter(status=status_filter)
    if search_query:
        complaints = complaints.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(complaint_no__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(complaints.order_by('-created_at'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_choices': Complaint.STATUS_CHOICES,
        'role': role,
        'filters': {
            'status': status_filter,
            'search': search_query,
        }
    }
    
    return render(request, 'complaints/complaint_list.html', context)


@login_required
def complaint_detail(request, complaint_no):
    """Complaint detail view"""
    complaint = get_object_or_404(Complaint, complaint_no=complaint_no)
    user_profile = getattr(request.user, 'profile', None)
    role = user_profile.role if user_profile else 'student'
    
    # Check permissions
    if role == 'student' and complaint.user != request.user:
        raise Http404("Complaint not found")
    elif role == 'faculty' and complaint.assigned_to != request.user and complaint.user != request.user and not request.user.is_staff:
        raise Http404("Complaint not found")
    elif role == 'hod' and complaint.assigned_to != request.user and not request.user.is_staff:
        raise Http404("Complaint not found")
    
    # Get complaint history
    history = complaint.history.all().order_by('-timestamp')
    
    # Get feedback if exists
    try:
        feedback = complaint.feedback
    except Feedback.DoesNotExist:
        feedback = None
    
    context = {
        'complaint': complaint,
        'history': history,
        'feedback': feedback,
        'role': role,
        'can_edit': (
            role == 'admin' or 
            (role == 'hod' and complaint.assigned_to == request.user) or
            (role == 'faculty' and (complaint.assigned_to == request.user or complaint.user == request.user)) or
            (role == 'student' and complaint.user == request.user and complaint.status == 'PENDING')
        ),
        'can_assign': role == 'admin',
        'can_feedback': (
            complaint.user == request.user and 
            complaint.status == 'RESOLVED' and 
            not feedback and
            role in ['student', 'faculty']
        ),
    }
    
    return render(request, 'complaints/complaint_detail.html', context)


@login_required
def create_complaint(request):
    """Create new complaint"""
    user_profile = getattr(request.user, 'profile', None)
    
    if not user_profile or user_profile.role not in ['student', 'faculty']:
        messages.error(request, "Only students and faculty can create complaints.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.user = request.user
            complaint.save()
            
            # Create history entry
            ComplaintHistory.objects.create(
                complaint=complaint,
                changed_by=request.user,
                from_status='',
                to_status='PENDING',
                remarks='Complaint created'
            )
            
            # Send notification to admin
            admin_users = User.objects.filter(profile__role='admin')
            for admin in admin_users:
                Notification.objects.create(
                    user=admin,
                    message=f"New complaint {complaint.complaint_no} created by {request.user.get_full_name() or request.user.username}"
                )
            
            # If complaint is from faculty, also notify the assigned HOD
            if user_profile.role == 'faculty' and complaint.assigned_to:
                Notification.objects.create(
                    user=complaint.assigned_to,
                    message=f"New complaint {complaint.complaint_no} created by faculty {request.user.get_full_name() or request.user.username} and assigned to you"
                )
            
            messages.success(request, f"Complaint {complaint.complaint_no} created successfully!")
            return redirect('complaint_detail', complaint_no=complaint.complaint_no)
    else:
        form = ComplaintForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'complaints/create_complaint.html', context)


@login_required
def update_complaint(request, complaint_no):
    """Update complaint status/details"""
    complaint = get_object_or_404(Complaint, complaint_no=complaint_no)
    user_profile = getattr(request.user, 'profile', None)
    role = user_profile.role if user_profile else 'student'
    
    # Check permissions
    can_edit = (
        role == 'admin' or 
        (role == 'faculty' and complaint.assigned_to == request.user) or
        (role == 'student' and complaint.user == request.user and complaint.status == 'PENDING')
    )
    
    if not can_edit:
        messages.error(request, "You don't have permission to edit this complaint.")
        return redirect('complaint_detail', complaint_no=complaint_no)
    
    if request.method == 'POST':
        old_status = complaint.status
        old_assigned_to = complaint.assigned_to
        
        # Update fields based on role
        if role == 'admin':
            complaint.status = request.POST.get('status', complaint.status)
            complaint.admin_remarks = request.POST.get('admin_remarks', complaint.admin_remarks)
        elif role == 'hod':
            complaint.status = request.POST.get('status', complaint.status)
            complaint.remarks = request.POST.get('remarks', complaint.remarks)
        elif role == 'faculty':
            # Faculty can update if assigned to them or if it's their own complaint
            if complaint.assigned_to == request.user:
                complaint.status = request.POST.get('status', complaint.status)
                complaint.remarks = request.POST.get('remarks', complaint.remarks)
            elif complaint.user == request.user and complaint.status == 'PENDING':
                # Faculty can edit their own pending complaints
                complaint.title = request.POST.get('title', complaint.title)
                complaint.description = request.POST.get('description', complaint.description)
        else:  # student
            if complaint.status == 'PENDING':
                complaint.title = request.POST.get('title', complaint.title)
                complaint.description = request.POST.get('description', complaint.description)
        
        complaint.save()
        
        # Create history entry if status changed
        if old_status != complaint.status:
            ComplaintHistory.objects.create(
                complaint=complaint,
                changed_by=request.user,
                from_status=old_status,
                to_status=complaint.status,
                remarks=request.POST.get('remarks', '')
            )
            
            # Send notification to user
            Notification.objects.create(
                user=complaint.user,
                message=f"Complaint {complaint.complaint_no} status updated to {complaint.get_status_display()}"
            )
            
            # Send email notification
            try:
                send_mail(
                    f'Complaint {complaint.complaint_no} Status Update',
                    f'Your complaint "{complaint.title}" status has been updated to {complaint.get_status_display()}.',
                    settings.DEFAULT_FROM_EMAIL,
                    [complaint.user.email],
                    fail_silently=True,
                )
            except Exception as e:
                logger.error(f"Failed to send email notification: {e}")
        
        messages.success(request, "Complaint updated successfully!")
        return redirect('complaint_detail', complaint_no=complaint_no)
    
    context = {
        'complaint': complaint,
        'role': role,
        'status_choices': Complaint.STATUS_CHOICES,
    }
    
    return render(request, 'complaints/update_complaint.html', context)


@login_required
def assign_complaint(request, complaint_no):
    """Assign complaint to faculty (admin only)"""
    if not request.user.is_staff:
        messages.error(request, "Only administrators can assign complaints.")
        return redirect('dashboard')
    
    complaint = get_object_or_404(Complaint, complaint_no=complaint_no)
    
    if request.method == 'POST':
        faculty_id = request.POST.get('assigned_to')
        remarks = request.POST.get('remarks', '')
        
        if faculty_id:
            faculty = get_object_or_404(User, id=faculty_id)
            old_assigned_to = complaint.assigned_to
            complaint.assigned_to = faculty
            complaint.save()
            
            # Create history entry
            ComplaintHistory.objects.create(
                complaint=complaint,
                changed_by=request.user,
                from_status=complaint.status,
                to_status=complaint.status,
                remarks=f"Assigned to {faculty.get_full_name() or faculty.username}. {remarks}"
            )
            
            # Send notification to faculty
            Notification.objects.create(
                user=faculty,
                message=f"Complaint {complaint.complaint_no} assigned to you"
            )
            
            # Send notification to user
            Notification.objects.create(
                user=complaint.user,
                message=f"Complaint {complaint.complaint_no} assigned to faculty"
            )
            
            # Send email notifications
            try:
                send_mail(
                    f'Complaint {complaint.complaint_no} Assignment',
                    f'Complaint "{complaint.title}" has been assigned to you.',
                    settings.DEFAULT_FROM_EMAIL,
                    [faculty.email],
                    fail_silently=True,
                )
            except Exception as e:
                logger.error(f"Failed to send email notification: {e}")
            
            messages.success(request, f"Complaint assigned to {faculty.get_full_name() or faculty.username}")
        else:
            messages.error(request, "Please select a faculty member.")
    
    # Get available faculty and HOD for assignment
    faculty_members = User.objects.filter(profile__role__in=['faculty', 'hod'])
    
    context = {
        'complaint': complaint,
        'faculty_members': faculty_members,
    }
    
    return render(request, 'complaints/assign_complaint.html', context)


@login_required
def add_feedback(request, complaint_no):
    """Add feedback for resolved complaint"""
    complaint = get_object_or_404(Complaint, complaint_no=complaint_no)
    
    # Check if user can add feedback
    if (complaint.user != request.user or 
        complaint.status != 'RESOLVED' or 
        hasattr(complaint, 'feedback')):
        messages.error(request, "You cannot add feedback for this complaint.")
        return redirect('complaint_detail', complaint_no=complaint_no)
    
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.complaint = complaint
            feedback.user = request.user
            feedback.save()
            
            messages.success(request, "Feedback submitted successfully!")
            return redirect('complaint_detail', complaint_no=complaint_no)
    else:
        form = FeedbackForm()
    
    context = {
        'complaint': complaint,
        'form': form,
    }
    
    return render(request, 'complaints/add_feedback.html', context)


def register(request):
    """User registration"""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            user_id = form.cleaned_data['user_id']
            password = form.cleaned_data['password']
            department = form.cleaned_data['department']
            user_type = form.cleaned_data['user_type']
            category = form.cleaned_data.get('category') or ''
            
            # Create user
            user = User.objects.create_user(
                username=username,
                password=password,
                email=form.cleaned_data.get('email', '')
            )
            
            # Create profile
            profile = UserProfile.objects.create(
                user=user,
                role=user_type,
                department=department,
                phone=form.cleaned_data.get('phone', ''),
                age=form.cleaned_data.get('age')
            )
            if user_type in ['faculty', 'hod'] and category:
                profile.category = category
                profile.save(update_fields=['category'])
            
            # Add to appropriate group
            if user_type == 'faculty':
                group_name = 'Faculty'
            elif user_type == 'hod':
                group_name = 'HOD'
            else:
                group_name = 'Student'
            group, _ = Group.objects.get_or_create(name=group_name)
            user.groups.add(group)
            
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('dashboard')
    else:
        form = UserRegisterForm()
    
    return render(request, 'complaints/register.html', {'form': form})


def custom_logout(request):
    """Logout and redirect to login (handles both GET and POST)"""
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('login')


# API Views
class ComplaintViewSet(viewsets.ModelViewSet):
    """API viewset for complaints"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'assigned_to', 'user']
    search_fields = ['title', 'description', 'complaint_no']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter complaints based on user role"""
        user_profile = getattr(self.request.user, 'profile', None)
        role = user_profile.role if user_profile else 'student'
        
        if role == 'admin':
            return Complaint.objects.all()
        elif role == 'hod':
            return Complaint.objects.filter(assigned_to=self.request.user)
        elif role == 'faculty':
            return Complaint.objects.filter(
                Q(assigned_to=self.request.user) | Q(user=self.request.user)
            )
        else:  # student
            return Complaint.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return ComplaintListSerializer
        elif self.action == 'create':
            return ComplaintCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ComplaintUpdateSerializer
        else:
            return ComplaintDetailSerializer
    
    def perform_create(self, serializer):
        """Create complaint with user"""
        user_profile = getattr(self.request.user, 'profile', None)
        if not user_profile or user_profile.role not in ['student', 'faculty']:
            raise PermissionError("Only students and faculty can create complaints")
        
        complaint = serializer.save(user=self.request.user)
        
        # Create history entry
        ComplaintHistory.objects.create(
            complaint=complaint,
            changed_by=self.request.user,
            from_status='',
            to_status='PENDING',
            remarks='Complaint created via API'
        )
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign complaint to faculty"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Only administrators can assign complaints'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        complaint = self.get_object()
        serializer = ComplaintAssignmentSerializer(data=request.data)
        
        if serializer.is_valid():
            faculty = serializer.validated_data['assigned_to']
            remarks = serializer.validated_data.get('remarks', '')
            
            old_assigned_to = complaint.assigned_to
            complaint.assigned_to = faculty
            complaint.save()
            
            # Create history entry
            ComplaintHistory.objects.create(
                complaint=complaint,
                changed_by=request.user,
                from_status=complaint.status,
                to_status=complaint.status,
                remarks=f"Assigned to {faculty.get_full_name() or faculty.username}. {remarks}"
            )
            
            return Response({'message': 'Complaint assigned successfully'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get complaint statistics"""
        complaint = self.get_object()
        
        stats = {
            'total_updates': complaint.history.count(),
            'days_since_created': (timezone.now() - complaint.created_at).days,
            'days_since_resolved': (timezone.now() - complaint.resolved_at).days if complaint.resolved_at else None,
        }
        
        return Response(stats)


class FeedbackViewSet(viewsets.ModelViewSet):
    """API viewset for feedback"""
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter feedback based on user role"""
        user_profile = getattr(self.request.user, 'profile', None)
        role = user_profile.role if user_profile else 'student'
        
        if role == 'admin':
            return Feedback.objects.all()
        else:
            return Feedback.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Create feedback with user"""
        complaint_no = self.request.data.get('complaint')
        complaint = get_object_or_404(Complaint, complaint_no=complaint_no)
        
        # Check if user can add feedback
        if (complaint.user != self.request.user or 
            complaint.status != 'RESOLVED' or 
            hasattr(complaint, 'feedback')):
            raise PermissionError("You cannot add feedback for this complaint")
        
        serializer.save(user=self.request.user, complaint=complaint)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """API viewset for notifications"""
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'message': 'Notification marked as read'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def complaint_stats(request):
    """Get complaint statistics"""
    user_profile = getattr(request.user, 'profile', None)
    role = user_profile.role if user_profile else 'student'
    
    # Base queryset based on role
    if role == 'admin':
        complaints = Complaint.objects.all()
    elif role == 'hod':
        complaints = Complaint.objects.filter(assigned_to=request.user)
    elif role == 'faculty':
        complaints = Complaint.objects.filter(
            Q(assigned_to=request.user) | Q(user=request.user)
        )
    else:  # student
        complaints = Complaint.objects.filter(user=request.user)
    
    # Calculate statistics
    stats = {
        'total_complaints': complaints.count(),
        'pending_complaints': complaints.filter(status='PENDING').count(),
        'in_progress_complaints': complaints.filter(status='IN_PROGRESS').count(),
        'resolved_complaints': complaints.filter(status='RESOLVED').count(),
        'closed_complaints': complaints.filter(status='CLOSED').count(),
    }
    
    # Calculate average resolution time
    resolved_complaints = complaints.filter(status='RESOLVED', resolved_at__isnull=False)
    if resolved_complaints.exists():
        resolution_times = []
        for complaint in resolved_complaints:
            resolution_time = complaint.resolved_at - complaint.created_at
            resolution_times.append(resolution_time)
        
        if resolution_times:
            avg_resolution_time = sum(resolution_times, timedelta()) / len(resolution_times)
            stats['avg_resolution_time'] = avg_resolution_time
    
    # Complaints by month (last 12 months)
    month_stats = {}
    for i in range(12):
        month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
        month_end = month_start + timedelta(days=30)
        count = complaints.filter(created_at__range=[month_start, month_end]).count()
        month_stats[month_start.strftime('%Y-%m')] = count
    stats['complaints_by_month'] = month_stats
    
    serializer = ComplaintStatsSerializer(stats)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def export_complaints(request):
    """Export complaints to CSV/PDF"""
    user_profile = getattr(request.user, 'profile', None)
    role = user_profile.role if user_profile else 'student'
    
    if role != 'admin':
        return Response({'error': 'Only administrators can export complaints'}, status=status.HTTP_403_FORBIDDEN)
    
    # Get filter parameters
    from_date = request.data.get('from_date')
    to_date = request.data.get('to_date')
    status_filter = request.data.get('status')
    format_type = request.data.get('format', 'csv')
    
    # Build queryset
    complaints = Complaint.objects.all()
    
    if from_date:
        complaints = complaints.filter(created_at__date__gte=from_date)
    if to_date:
        complaints = complaints.filter(created_at__date__lte=to_date)
    if status_filter:
        complaints = complaints.filter(status=status_filter)
    
    if format_type == 'csv':
        import csv
        import io
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="complaints_{timezone.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Complaint No', 'Title', 'Status', 'User', 'Assigned To',
            'Created At', 'Resolved At'
        ])
        
        for complaint in complaints:
            writer.writerow([
                complaint.complaint_no,
                complaint.title,
                complaint.get_status_display(),
                complaint.user.get_full_name() or complaint.user.username,
                complaint.assigned_to.get_full_name() if complaint.assigned_to else '',
                complaint.created_at.strftime('%Y-%m-%d %H:%M'),
                complaint.resolved_at.strftime('%Y-%m-%d %H:%M') if complaint.resolved_at else '',
            ])
        
        return response
    
    elif format_type == 'pdf':
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        import io
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title = Paragraph("Complaints Report", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Data table
        data = [['Complaint No', 'Title', 'Status', 'User', 'Created At']]
        
        for complaint in complaints[:100]:  # Limit to 100 for PDF
            data.append([
                complaint.complaint_no,
                complaint.title[:30] + '...' if len(complaint.title) > 30 else complaint.title,
                complaint.get_status_display(),
                complaint.user.get_full_name() or complaint.user.username,
                complaint.created_at.strftime('%Y-%m-%d'),
            ])
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        doc.build(story)
        
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="complaints_{timezone.now().strftime("%Y%m%d")}.pdf"'
        
        return response
    
    return Response({'error': 'Invalid format'}, status=status.HTTP_400_BAD_REQUEST)


# Legacy views for backward compatibility
def complaint_list_legacy(request):
    """Legacy complaint list view"""
    return complaint_list(request)


def create_complaint_legacy(request):
    """Legacy create complaint view"""
    return create_complaint(request)


def update_status_legacy(request, complaint_id):
    """Legacy update status view"""
    complaint = get_object_or_404(Complaint, id=complaint_id)
    return redirect('complaint_detail', complaint_no=complaint.complaint_no)


def faculty_dashboard_legacy(request):
    """Legacy faculty dashboard"""
    return dashboard(request)


def student_complaints_legacy(request):
    """Legacy student complaints view"""
    return complaint_list(request)