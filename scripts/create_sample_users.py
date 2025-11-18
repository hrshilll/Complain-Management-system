# Run this inside Django shell:
# python manage.py shell < create_sample_users.py

from django.contrib.auth.models import User, Group
from complaints.models import Department  # Adjust if your model name/path differs
from random import choice

# Departments
departments = ["Computer Science", "Electrical", "Mechanical", "Civil", "Information Technology"]
for dep_name in departments:
    Department.objects.get_or_create(name=dep_name)

print("✅ Departments created or already exist.")

# Create Groups (if not already created)
student_group, _ = Group.objects.get_or_create(name="Student")
faculty_group, _ = Group.objects.get_or_create(name="Faculty")

# Helper to generate email-friendly username
def username_from_name(name):
    return name.lower().replace(" ", "")

# Student names
student_names = [
    "Aarav Patel", "Isha Sharma", "Rohan Mehta", "Sneha Singh", "Karan Desai",
    "Priya Nair", "Ananya Verma", "Vikas Gupta", "Diya Malhotra", "Sahil Bansal",
    "Nisha Rao", "Aditya Joshi", "Meera Iyer", "Raj Chauhan", "Tanvi Shah"
]

# Faculty names
faculty_names = [
    "Dr. Neha Kapoor", "Prof. Arjun Sinha", "Dr. Ritu Menon", "Prof. Manish Kumar", "Dr. Kavita Joshi"
]

# Create students
for i, name in enumerate(student_names, start=1):
    username = username_from_name(name)
    email = f"{username}@student.edu.in"
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
        print(f"👩‍🎓 Created student: {name} ({email}) - Dept: {dept.name}")

# Create faculty
for i, name in enumerate(faculty_names, start=1):
    username = username_from_name(name)
    email = f"{username}@faculty.edu.in"
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
        print(f"👨‍🏫 Created faculty: {name} ({email}) - Dept: {dept.name}")

print("\n🎉 All users created successfully!")
print("Login credentials examples:")
print(" - Student: aaravpatel@student.edu.in / student123")
print(" - Faculty: drnehakapoor@faculty.edu.in / faculty123")