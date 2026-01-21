from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from complaints.models import UserProfile
import random


class Command(BaseCommand):
    help = 'Reset all users and populate with dummy data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Deleting all existing users (except superusers)...'))
        
        # Delete all non-superuser users (cascade will delete profiles)
        non_superusers = User.objects.filter(is_superuser=False)
        count = non_superusers.count()
        non_superusers.delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {count} non-superuser accounts'))
        
        # Ensure UserProfile is clean (safety check)
        UserProfile.objects.filter(user__is_superuser=False).delete()
        
        password = 'QWER@1234'
        
        # Indian names
        hod_first_names = ['Rajesh', 'Priya', 'Amit', 'Sneha', 'Vikram', 'Anjali']
        hod_last_names = ['Kumar', 'Sharma', 'Patel', 'Singh', 'Reddy', 'Nair']
        hod_departments = ['CSE', 'IT', 'CE', 'Mechanical', 'Civil', 'EC']
        
        faculty_first_names = ['Ramesh', 'Sunita', 'Deepak', 'Kavita', 'Manoj', 'Pooja', 
                              'Suresh', 'Meera', 'Anil', 'Divya', 'Ravi', 'Shilpa',
                              'Nitin', 'Rekha', 'Kiran', 'Swati', 'Ajay', 'Neha']
        faculty_last_names = ['Gupta', 'Verma', 'Jain', 'Malhotra', 'Agarwal', 'Kapoor',
                             'Mehta', 'Bansal', 'Goyal', 'Chopra', 'Saxena', 'Tiwari',
                             'Joshi', 'Pandey', 'Mishra', 'Yadav', 'Shukla', 'Dubey']
        
        student_first_names = ['Arjun', 'Sakshi', 'Rohit', 'Pooja', 'Karan', 'Ananya', 
                              'Vishal', 'Isha', 'Rahul', 'Kritika', 'Aditya', 'Shreya',
                              'Mohit', 'Tanvi', 'Siddharth', 'Aishwarya', 'Harsh', 'Nidhi',
                              'Yash', 'Riya', 'Kunal', 'Pragya', 'Varun', 'Sneha', 'Aman']
        student_last_names = ['Sharma', 'Patel', 'Kumar', 'Singh', 'Reddy', 'Nair', 'Iyer',
                             'Menon', 'Pillai', 'Nair', 'Krishnan', 'Rao', 'Desai', 'Shah',
                             'Mehta', 'Gandhi', 'Bose', 'Banerjee', 'Chatterjee', 'Mukherjee',
                             'Das', 'Roy', 'Sengupta', 'Dutta', 'Basu']
        
        departments = ['CSE', 'IT', 'CE', 'Mechanical', 'Civil', 'EC', 'EEE', 'ECE']
        categories = ['academic', 'it', 'lab', 'library', 'maintenance', 'administration']
        
        # Create 6 HOD users
        self.stdout.write(self.style.WARNING('Creating 6 HOD users...'))
        for i in range(6):
            first_name = hod_first_names[i]
            last_name = hod_last_names[i]
            department = hod_departments[i]
            username = f"{first_name.lower()}.hod.{department.lower()}"
            email = f"{first_name.lower()}.hod.{department.lower()}@university.edu"
            phone = f"9{random.randint(100000000, 999999999)}"
            
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            UserProfile.objects.create(
                user=user,
                role='hod',
                department=department,
                phone=phone,
                age=random.randint(40, 55),
                category=random.choice(categories)
            )
            
            group, _ = Group.objects.get_or_create(name='HOD')
            user.groups.add(group)
            
            self.stdout.write(f'  Created HOD: {first_name} {last_name} ({department})')
        
        # Create 18 Faculty users
        self.stdout.write(self.style.WARNING('Creating 18 Faculty users...'))
        for i in range(18):
            first_name = faculty_first_names[i]
            last_name = faculty_last_names[i]
            department = random.choice(departments)
            category = random.choice(categories)
            username = f"{first_name.lower()}.{last_name.lower()}.{i+1}"
            email = f"{first_name.lower()}.{last_name.lower()}@university.edu"
            phone = f"9{random.randint(100000000, 999999999)}"
            
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            UserProfile.objects.create(
                user=user,
                role='faculty',
                department=department,
                phone=phone,
                age=random.randint(28, 45),
                category=category
            )
            
            group, _ = Group.objects.get_or_create(name='Faculty')
            user.groups.add(group)
            
            self.stdout.write(f'  Created Faculty: {first_name} {last_name} ({department})')
        
        # Create 25 Student users
        self.stdout.write(self.style.WARNING('Creating 25 Student users...'))
        for i in range(25):
            first_name = student_first_names[i]
            last_name = student_last_names[i]
            department = random.choice(departments)
            roll_no = f"{random.randint(20, 24)}{department}{random.randint(100, 999)}"
            username = f"{first_name.lower()}.{roll_no.lower()}"
            email = f"{first_name.lower()}.{roll_no.lower()}@college.edu"
            phone = f"9{random.randint(100000000, 999999999)}" if random.random() > 0.3 else None
            
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            UserProfile.objects.create(
                user=user,
                role='student',
                department=department,
                phone=phone,
                age=random.randint(18, 23)
            )
            
            group, _ = Group.objects.get_or_create(name='Student')
            user.groups.add(group)
            
            self.stdout.write(f'  Created Student: {first_name} {last_name} ({department})')
        
        # Summary
        total_users = User.objects.filter(is_superuser=False).count()
        hod_count = UserProfile.objects.filter(role='hod').count()
        faculty_count = UserProfile.objects.filter(role='faculty').count()
        student_count = UserProfile.objects.filter(role='student').count()
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('RESET COMPLETE'))
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(self.style.SUCCESS(f'Total Users: {total_users}'))
        self.stdout.write(self.style.SUCCESS(f'  - HOD: {hod_count}'))
        self.stdout.write(self.style.SUCCESS(f'  - Faculty: {faculty_count}'))
        self.stdout.write(self.style.SUCCESS(f'  - Student: {student_count}'))
        self.stdout.write(self.style.SUCCESS(f'\nAll passwords set to: {password}'))

