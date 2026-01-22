"""
Admin views for PDF export functionality
"""
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.utils import timezone
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import io
from .models import Complaint


@staff_member_required
def export_complaints_pdf(request):
    """
    Export complaints to PDF with month/week filters
    Supports:
    - Weekly: Last 7 days
    - Monthly: Current month or specific month
    - Custom date range
    """
    # Get filter parameters
    filter_type = request.GET.get('filter', 'month')  # week, month, custom
    year = request.GET.get('year', timezone.now().year)
    month = request.GET.get('month', timezone.now().month)
    week_start = request.GET.get('week_start', None)
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)
    
    # Determine date range
    today = timezone.now()
    
    if filter_type == 'week':
        if week_start:
            try:
                start = datetime.strptime(week_start, '%Y-%m-%d')
                start = timezone.make_aware(start)
            except:
                start = today - timedelta(days=7)
        else:
            start = today - timedelta(days=7)
        end = today
        title = f"Weekly Complaint Report ({start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')})"
        
    elif filter_type == 'month':
        try:
            year = int(year)
            month = int(month)
            start = timezone.make_aware(datetime(year, month, 1))
            if month == 12:
                end = timezone.make_aware(datetime(year + 1, 1, 1)) - timedelta(days=1)
            else:
                end = timezone.make_aware(datetime(year, month + 1, 1)) - timedelta(days=1)
        except:
            start = today.replace(day=1)
            end = today
        title = f"Monthly Complaint Report ({start.strftime('%B %Y')})"
        
    elif filter_type == 'custom' and start_date and end_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            start = timezone.make_aware(start)
            end = timezone.make_aware(end)
            end = end.replace(hour=23, minute=59, second=59)
        except:
            start = today - timedelta(days=30)
            end = today
        title = f"Complaint Report ({start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')})"
    else:
        # Default to current month
        start = today.replace(day=1)
        end = today
        title = f"Monthly Complaint Report ({start.strftime('%B %Y')})"
    
    # Filter complaints
    complaints = Complaint.objects.filter(
        created_at__gte=start,
        created_at__lte=end
    ).select_related('user', 'assigned_to', 'category', 'subcategory').order_by('-created_at')
    
    # Create PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=18,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=1  # Center
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#333333'),
        spaceAfter=12
    )
    
    # Title
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Summary statistics
    stats_data = [
        ['Total Complaints', str(complaints.count())],
        ['Pending', str(complaints.filter(status='PENDING').count())],
        ['Processing', str(complaints.filter(status='PROCESSING').count())],
        ['Resolved', str(complaints.filter(status='RESOLVED').count())],
        ['Rejected', str(complaints.filter(status='REJECTED').count())],
    ]
    
    stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#4dd0e1')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
        ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#f0f0f0')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    
    story.append(Paragraph("Summary Statistics", heading_style))
    story.append(stats_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Complaints table
    story.append(Paragraph("Complaints Details", heading_style))
    
    # Table headers
    data = [[
        'Complaint No',
        'Title',
        'Category',
        'Status',
        'User',
        'Assigned To',
        'Priority',
        'Created Date'
    ]]
    
    # Table data
    for complaint in complaints:
        data.append([
            complaint.complaint_no or 'N/A',
            complaint.title[:40] + '...' if len(complaint.title) > 40 else complaint.title,
            complaint.category.name if complaint.category else 'N/A',
            complaint.get_status_display(),
            complaint.user.get_full_name() or complaint.user.username,
            complaint.assigned_to.get_full_name() if complaint.assigned_to else 'Unassigned',
            complaint.priority or 'N/A',
            complaint.created_at.strftime('%Y-%m-%d') if complaint.created_at else 'N/A',
        ])
    
    if len(data) == 1:  # Only headers, no data
        data.append(['No complaints found for the selected period.', '', '', '', '', '', '', ''])
    
    # Create table
    table = Table(data, colWidths=[1*inch, 2*inch, 1*inch, 0.8*inch, 1*inch, 1*inch, 0.7*inch, 0.8*inch])
    table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a1a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        # Data rows
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        # Grid
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        # Alternating row colors
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 0.2*inch))
    
    # Footer
    footer_text = f"Generated on {today.strftime('%Y-%m-%d %H:%M:%S')} | Total Records: {complaints.count()}"
    story.append(Paragraph(footer_text, styles['Normal']))
    
    # Build PDF
    doc.build(story)
    
    # Create response
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    filename = f"complaints_report_{filter_type}_{today.strftime('%Y%m%d_%H%M%S')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response
