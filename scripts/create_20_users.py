# Enhanced user creation script for 20 users (15 students + 5 faculty)
# Run this inside Django shell:
# python3 manage.py shell < create_20_users.py

from django.contrib.auth.models import User, Group
from complaints.models import Department, UserProfile, FacultyProfile, StudentProfile
from random import choice
import random

# Departments
departments = [
    "Computer Science and Engineering",
    "Electrical and Electronics Engineering", 
    "Mechanical Engineering",
    "Civil Engineering",
    "Information Technology",
    "Electronics and Communication Engineering",
    "Chemical Engineering",
    "Aerospace Engineering"
]

# Create departments
for dep_name in departments:
    Department.objects.get_or_create(name=dep_name)

print("✅ Departments created or already exist.")

# Create Groups (if not already created)
student_group, _ = Group.objects.get_or_create(name="Student")
faculty_group, _ = Group.objects.get_or_create(name="Faculty")

# Helper to generate email-friendly username
def username_from_name(name):
    return name.lower().replace(" ", "").replace(".", "").replace("dr", "").replace("prof", "")

# Student names with diverse backgrounds
student_names = [
    "Aarav Patel", "Isha Sharma", "Rohan Mehta", "Sneha Singh", "Karan Desai",
    "Priya Nair", "Ananya Verma", "Vikas Gupta", "Diya Malhotra", "Sahil Bansal",
    "Nisha Rao", "Aditya Joshi", "Meera Iyer", "Raj Chauhan", "Tanvi Shah"
]

# Faculty names with titles
faculty_names = [
    "Dr. Neha Kapoor", "Prof. Arjun Sinha", "Dr. Ritu Menon", "Prof. Manish Kumar", "Dr. Kavita Joshi"
]

# Student ID format: STU2024001, STU2024002, etc.
# Faculty ID format: FAC2024001, FAC2024002, etc.

print("\n🎓 Creating 15 Students...")
print("=" * 50)

# Create students
for i, name in enumerate(student_names, start=1):
    username = username_from_name(name)
    email = f"{username}@student.edu.in"
    student_id = f"STU2024{i:03d}"
    dept = Department.objects.order_by("?").first()
    
    user, created = User.objects.get_or_create(username=username, defaults={
        "first_name": name.split()[0],
        "last_name": name.split()[-1],
        "email": email,
    })
    
    if created:
        user.set_password("student123")
        user.save()
        user.groups.add(student_group)
        
        # Create UserProfile
        UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'role': 'student',
                'department': dept.name,
                'phone': f"9{random.randint(10000000, 99999999)}"
            }
        )
        
        # Create StudentProfile for legacy compatibility
        StudentProfile.objects.get_or_create(
            user=user,
            defaults={
                'student_id': student_id,
                'department': dept
            }
        )
        
        print(f"👩‍🎓 Student {i:2d}: {name:<20} | ID: {student_id} | Email: {email:<30} | Dept: {dept.name}")
    else:
        print(f"⚠️  Student {i:2d}: {name} already exists")

print("\n👨‍🏫 Creating 5 Faculty...")
print("=" * 50)

# Create faculty
for i, name in enumerate(faculty_names, start=1):
    username = username_from_name(name)
    email = f"{username}@faculty.edu.in"
    faculty_id = f"FAC2024{i:03d}"
    dept = Department.objects.order_by("?").first()
    
    user, created = User.objects.get_or_create(username=username, defaults={
        "first_name": name.split()[0],
        "last_name": name.split()[-1],
        "email": email,
    })
    
    if created:
        user.set_password("faculty123")
        user.save()
        user.groups.add(faculty_group)
        
        # Create UserProfile
        UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'role': 'faculty',
                'department': dept.name,
                'phone': f"9{random.randint(10000000, 99999999)}"
            }
        )
        
        # Create FacultyProfile for legacy compatibility
        FacultyProfile.objects.get_or_create(
            user=user,
            defaults={
                'faculty_id': faculty_id,
                'department': dept
            }
        )
        
        print(f"👨‍🏫 Faculty {i}: {name:<20} | ID: {faculty_id} | Email: {email:<30} | Dept: {dept.name}")
    else:
        print(f"⚠️  Faculty {i}: {name} already exists")

print("\n" + "=" * 60)
print("🎉 User Creation Summary")
print("=" * 60)
print(f"📊 Total Users Created: {User.objects.count()}")
print(f"👩‍🎓 Students: {User.objects.filter(groups__name='Student').count()}")
print(f"👨‍🏫 Faculty: {User.objects.filter(groups__name='Faculty').count()}")
print(f"🏢 Departments: {Department.objects.count()}")

print("\n🔐 Login Credentials Examples:")
print("-" * 40)
print("Students:")
print("  • aaravpatel@student.edu.in / student123")
print("  • ishasharma@student.edu.in / student123")
print("  • rohanmehta@student.edu.in / student123")

print("\nFaculty:")
print("  • nehakapoor@faculty.edu.in / faculty123")
print("  • arjunsinha@faculty.edu.in / faculty123")
print("  • ritumenon@faculty.edu.in / faculty123")

print("\n🌐 Access the system at: http://localhost:8000/")
print("📱 Admin panel: http://localhost:8000/admin/")
