#!/usr/bin/env python3
"""
Script to populate the database with sample data for the Complaint Management System.
"""

import os
import sys
import django
from datetime import datetime, timedelta
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'complaint_system.settings')
django.setup()

from django.contrib.auth.models import User, Group
from complaints.models import (
    UserProfile, Category, SubCategory, LocationState, 
    Complaint, ComplaintHistory, Feedback, Notification,
    Department
)

def create_sample_data():
    """Create sample data for the CMS"""
    print("Creating sample data...")
    
    # Create departments
    departments = [
        'Computer Science',
        'Electrical Engineering',
        'Mechanical Engineering',
        'Civil Engineering',
        'Mathematics',
        'Physics',
        'Chemistry',
        'Biology',
        'Administration',
        'Library'
    ]
    
    dept_objects = []
    for dept_name in departments:
        dept, created = Department.objects.get_or_create(name=dept_name)
        dept_objects.append(dept)
        if created:
            print(f"Created department: {dept_name}")
    
    # Create categories
    categories_data = [
        ('Academic', 'Issues related to academics, courses, and curriculum'),
        ('Infrastructure', 'Problems with buildings, facilities, and equipment'),
        ('Administrative', 'Administrative procedures and policies'),
        ('IT Support', 'Computer and network related issues'),
        ('Library', 'Library services and resources'),
        ('Hostel', 'Hostel facilities and management'),
        ('Transport', 'Transportation services'),
        ('Cafeteria', 'Food services and cafeteria'),
        ('Sports', 'Sports facilities and activities'),
        ('General', 'General complaints and suggestions')
    ]
    
    category_objects = []
    for name, description in categories_data:
        category, created = Category.objects.get_or_create(name=name, defaults={'description': description})
        category_objects.append(category)
        if created:
            print(f"Created category: {name}")
    
    # Create subcategories
    subcategories_data = [
        ('Academic', [
            'Course Registration',
            'Grade Issues',
            'Exam Schedule',
            'Faculty Availability',
            'Course Material'
        ]),
        ('Infrastructure', [
            'Classroom Issues',
            'Laboratory Equipment',
            'Building Maintenance',
            'Power Supply',
            'Water Supply'
        ]),
        ('Administrative', [
            'Document Processing',
            'Fee Payment',
            'Certificate Issuance',
            'Admission Process',
            'Policy Clarification'
        ]),
        ('IT Support', [
            'Network Connectivity',
            'Software Issues',
            'Hardware Problems',
            'Email Services',
            'System Access'
        ]),
        ('Library', [
            'Book Availability',
            'Digital Resources',
            'Study Space',
            'Library Hours',
            'Research Support'
        ])
    ]
    
    subcategory_objects = []
    for cat_name, subcats in subcategories_data:
        try:
            category = Category.objects.get(name=cat_name)
            for subcat_name in subcats:
                subcat, created = SubCategory.objects.get_or_create(
                    category=category, 
                    name=subcat_name,
                    defaults={'description': f'Subcategory for {subcat_name}'}
                )
                subcategory_objects.append(subcat)
                if created:
                    print(f"Created subcategory: {subcat_name}")
        except Category.DoesNotExist:
            print(f"Category {cat_name} not found, skipping subcategories")
    
    # Create location states
    states_data = [
        ('Maharashtra', 'MH'),
        ('Karnataka', 'KA'),
        ('Tamil Nadu', 'TN'),
        ('Kerala', 'KL'),
        ('Delhi', 'DL'),
        ('Gujarat', 'GJ'),
        ('Rajasthan', 'RJ'),
        ('Punjab', 'PB'),
        ('Haryana', 'HR'),
        ('Uttar Pradesh', 'UP')
    ]
    
    state_objects = []
    for name, code in states_data:
        state, created = LocationState.objects.get_or_create(name=name, defaults={'code': code})
        state_objects.append(state)
        if created:
            print(f"Created state: {name}")
    
    # Create groups
    student_group, _ = Group.objects.get_or_create(name='Student')
    faculty_group, _ = Group.objects.get_or_create(name='Faculty')
    admin_group, _ = Group.objects.get_or_create(name='Admin')
    
    # Create admin users
    admin_users = [
        ('admin', 'admin@example.com', 'admin123', 'Administration'),
        ('superadmin', 'superadmin@example.com', 'superadmin123', 'Administration')
    ]
    
    for username, email, password, dept in admin_users:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': username.title(),
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            user.set_password(password)
            user.save()
            user.groups.add(admin_group)
            
            profile, _ = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'role': 'admin',
                    'department': dept,
                    'phone': f'+91-{random.randint(9000000000, 9999999999)}'
                }
            )
            print(f"Created admin user: {username}")
    
    # Create faculty users
    faculty_users = [
        ('dr_smith', 'dr.smith@example.com', 'faculty123', 'Computer Science'),
        ('prof_johnson', 'prof.johnson@example.com', 'faculty123', 'Electrical Engineering'),
        ('dr_williams', 'dr.williams@example.com', 'faculty123', 'Mechanical Engineering'),
        ('prof_brown', 'prof.brown@example.com', 'faculty123', 'Mathematics'),
        ('dr_davis', 'dr.davis@example.com', 'faculty123', 'Physics')
    ]
    
    faculty_objects = []
    for username, email, password, dept in faculty_users:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': username.split('_')[1].title(),
                'last_name': username.split('_')[2].title() if len(username.split('_')) > 2 else 'Professor'
            }
        )
        if created:
            user.set_password(password)
            user.save()
            user.groups.add(faculty_group)
            
            profile, _ = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'role': 'faculty',
                    'department': dept,
                    'phone': f'+91-{random.randint(9000000000, 9999999999)}'
                }
            )
            faculty_objects.append(user)
            print(f"Created faculty user: {username}")
    
    # Create student users
    student_users = [
        ('john_doe', 'john.doe@student.example.com', 'student123', 'Computer Science'),
        ('jane_smith', 'jane.smith@student.example.com', 'student123', 'Electrical Engineering'),
        ('mike_johnson', 'mike.johnson@student.example.com', 'student123', 'Mechanical Engineering'),
        ('sarah_williams', 'sarah.williams@student.example.com', 'student123', 'Mathematics'),
        ('david_brown', 'david.brown@student.example.com', 'student123', 'Physics'),
        ('lisa_davis', 'lisa.davis@student.example.com', 'student123', 'Computer Science'),
        ('tom_wilson', 'tom.wilson@student.example.com', 'student123', 'Electrical Engineering'),
        ('emma_moore', 'emma.moore@student.example.com', 'student123', 'Mechanical Engineering'),
        ('alex_taylor', 'alex.taylor@student.example.com', 'student123', 'Mathematics'),
        ('sophia_anderson', 'sophia.anderson@student.example.com', 'student123', 'Physics')
    ]
    
    student_objects = []
    for username, email, password, dept in student_users:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': username.split('_')[0].title(),
                'last_name': username.split('_')[1].title()
            }
        )
        if created:
            user.set_password(password)
            user.save()
            user.groups.add(student_group)
            
            profile, _ = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'role': 'student',
                    'department': dept,
                    'phone': f'+91-{random.randint(9000000000, 9999999999)}'
                }
            )
            student_objects.append(user)
            print(f"Created student user: {username}")
    
    # Create sample complaints
    complaint_titles = [
        'Network connectivity issues in Computer Lab',
        'Air conditioning not working in Library',
        'Course registration portal is down',
        'Water leakage in Hostel Block A',
        'Cafeteria food quality concerns',
        'Sports equipment maintenance required',
        'Transport bus schedule issues',
        'Grade calculation error in Mathematics course',
        'Library book availability problem',
        'Hostel WiFi connectivity issues',
        'Cafeteria payment system not working',
        'Sports complex lighting problems',
        'Transport bus overcrowding',
        'Course material not uploaded',
        'Hostel room maintenance required',
        'Library study space shortage',
        'Cafeteria hygiene concerns',
        'Sports equipment booking system down',
        'Transport bus driver behavior',
        'Course evaluation process issues',
        'Hostel security concerns',
        'Library digital resources access',
        'Cafeteria menu variety request',
        'Sports facility booking conflicts',
        'Transport bus timing accuracy',
        'Course assignment submission issues',
        'Hostel laundry service problems',
        'Library quiet study area noise',
        'Cafeteria pricing concerns',
        'Sports complex maintenance schedule'
    ]
    
    complaint_descriptions = [
        'The network connection in the computer lab is frequently dropping, making it difficult to complete assignments.',
        'The air conditioning system in the library has been malfunctioning for the past week, making it uncomfortable to study.',
        'Students are unable to register for courses due to portal downtime.',
        'There is a water leakage issue in Hostel Block A that needs immediate attention.',
        'The quality of food served in the cafeteria has deteriorated significantly.',
        'Several sports equipment items are in need of maintenance and replacement.',
        'The transport bus schedule is not being followed consistently.',
        'There appears to be an error in the grade calculation for the Mathematics course.',
        'Required books are not available in the library for the current semester courses.',
        'WiFi connectivity in the hostel is poor and frequently disconnects.',
        'The payment system in the cafeteria is not working properly.',
        'The lighting in the sports complex is inadequate for evening activities.',
        'The transport buses are overcrowded during peak hours.',
        'Course materials have not been uploaded to the learning management system.',
        'Several hostel rooms require maintenance work.',
        'There is insufficient study space in the library during exam periods.',
        'Hygiene standards in the cafeteria need improvement.',
        'The sports equipment booking system is experiencing technical issues.',
        'Some transport bus drivers are not following proper conduct.',
        'The course evaluation process needs to be more transparent.',
        'Security measures in the hostel need to be strengthened.',
        'Access to digital resources in the library is restricted.',
        'The cafeteria menu lacks variety and healthy options.',
        'There are conflicts in sports facility bookings.',
        'Transport bus timings are not accurate.',
        'Students are facing issues with assignment submission.',
        'The laundry service in the hostel is unreliable.',
        'Noise levels in the library quiet study area are too high.',
        'Cafeteria prices have increased without proper justification.',
        'The sports complex maintenance schedule is not being followed.'
    ]
    
    statuses = ['PENDING', 'IN_PROGRESS', 'RESOLVED', 'CLOSED']
    priorities = ['LOW', 'MEDIUM', 'HIGH']
    
    complaint_objects = []
    for i in range(30):
        # Generate complaint number
        today = datetime.now().date()
        date_str = today.strftime('%Y%m%d')
        complaint_no = f'CMP-{date_str}-{i+1:06d}'
        
        # Create complaint
        complaint = Complaint.objects.create(
            complaint_no=complaint_no,
            title=complaint_titles[i],
            description=complaint_descriptions[i],
            category=random.choice(category_objects),
            subcategory=random.choice(subcategory_objects) if subcategory_objects else None,
            state=random.choice(state_objects),
            user=random.choice(student_objects),
            assigned_to=random.choice(faculty_objects) if random.random() > 0.3 else None,
            status=random.choice(statuses),
            priority=random.choice(priorities),
            created_at=datetime.now() - timedelta(days=random.randint(1, 90)),
            remarks=f'Sample remark for complaint {complaint_no}',
            admin_remarks=f'Admin remark for complaint {complaint_no}' if random.random() > 0.5 else ''
        )
        
        # Set resolved_at if status is RESOLVED
        if complaint.status == 'RESOLVED':
            complaint.resolved_at = complaint.created_at + timedelta(days=random.randint(1, 30))
            complaint.save()
        
        complaint_objects.append(complaint)
        
        # Create history entries
        ComplaintHistory.objects.create(
            complaint=complaint,
            changed_by=complaint.user,
            from_status='',
            to_status='PENDING',
            remarks='Complaint created',
            timestamp=complaint.created_at
        )
        
        if complaint.assigned_to:
            ComplaintHistory.objects.create(
                complaint=complaint,
                changed_by=random.choice([u for u in User.objects.filter(profile__role='admin')]),
                from_status='PENDING',
                to_status='IN_PROGRESS',
                remarks=f'Assigned to {complaint.assigned_to.get_full_name()}',
                timestamp=complaint.created_at + timedelta(hours=random.randint(1, 24))
            )
        
        if complaint.status in ['RESOLVED', 'CLOSED']:
            ComplaintHistory.objects.create(
                complaint=complaint,
                changed_by=complaint.assigned_to or random.choice([u for u in User.objects.filter(profile__role='admin')]),
                from_status='IN_PROGRESS',
                to_status=complaint.status,
                remarks=f'Complaint {complaint.status.lower()}',
                timestamp=complaint.resolved_at or complaint.created_at + timedelta(days=random.randint(1, 30))
            )
        
        print(f"Created complaint: {complaint_no}")
    
    # Create sample feedback
    resolved_complaints = [c for c in complaint_objects if c.status == 'RESOLVED']
    for complaint in resolved_complaints[:10]:  # Create feedback for first 10 resolved complaints
        feedback = Feedback.objects.create(
            complaint=complaint,
            rating=random.randint(1, 5),
            comments=f'Sample feedback for complaint {complaint.complaint_no}. The issue was resolved satisfactorily.',
            user=complaint.user,
            created_at=complaint.resolved_at + timedelta(days=random.randint(1, 7))
        )
        print(f"Created feedback for complaint: {complaint.complaint_no}")
    
    # Create sample notifications
    notification_messages = [
        'New complaint assigned to you',
        'Complaint status updated',
        'New feedback received',
        'System maintenance scheduled',
        'Important announcement',
        'Deadline reminder',
        'Meeting scheduled',
        'Document ready for review',
        'Payment due reminder',
        'Event notification'
    ]
    
    all_users = list(User.objects.all())
    for i in range(50):
        user = random.choice(all_users)
        message = random.choice(notification_messages)
        notification = Notification.objects.create(
            user=user,
            message=message,
            is_read=random.choice([True, False]),
            created_at=datetime.now() - timedelta(days=random.randint(1, 30))
        )
        print(f"Created notification for user: {user.username}")
    
    print("\nSample data creation completed!")
    print(f"Created:")
    print(f"- {len(dept_objects)} departments")
    print(f"- {len(category_objects)} categories")
    print(f"- {len(subcategory_objects)} subcategories")
    print(f"- {len(state_objects)} states")
    print(f"- {len(faculty_objects)} faculty users")
    print(f"- {len(student_objects)} student users")
    print(f"- {len(complaint_objects)} complaints")
    print(f"- {len(Feedback.objects.all())} feedback entries")
    print(f"- {len(Notification.objects.all())} notifications")

if __name__ == '__main__':
    create_sample_data()
