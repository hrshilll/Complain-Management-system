
Complaint Management System (CMS)

A role-based Complaint Management System built with Django and Django REST Framework for educational institutions.
Designed to handle complaints end-to-end with clear workflows, audit trails, and secure access control.

This project was developed as a Semester 1 full-stack academic project, focusing on real-world system design rather than toy examples.

⸻

✨ Highlights
	•	Multi-role architecture (Admin, Faculty, Student)
	•	Complete complaint lifecycle management
	•	Secure file uploads & audit logs
	•	REST API for programmatic access
	•	Clean Django architecture with separation of concerns

Built like production software. Treated like a learning project.

⸻

🚀 Features

Core Functionality
	•	Multi-Role System
	•	Admin, Faculty, and Student roles
	•	Strict role-based permissions
	•	Complaint Workflow
	•	Create → Assign → Track → Resolve → Close
	•	Status flow: Pending → In Progress → Resolved → Closed
	•	Priority Handling
	•	Low / Medium / High priorities
	•	File Attachments
	•	PDFs, images, and documents
	•	Size limit: 10 MB per file
	•	Audit Trail
	•	Full history of complaint updates and actions
	•	Feedback System
	•	Students can rate and comment on resolved complaints
	•	Auto-Generated Complaint IDs
	•	Format: CMP-YYYYMMDD-XXXXXX

⸻

🧠 Technical Features
	•	Backend: Django 4.2+
	•	API: Django REST Framework (Token Authentication)
	•	Frontend: Server-rendered Django templates
	•	Database: SQLite (local development)
	•	Security: Django auth, CSRF protection, ORM safety
	•	Architecture: Modular apps, clean models, serializers

⸻

📋 Requirements
	•	Python 3.11+
	•	pip
	•	SQLite (bundled with Python)

⸻

🛠️ Installation & Setup

macOS / Linux

git clone https://github.com/hrshilll/Complain-Management-system.git
cd Complain-Management-system

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

Visit: http://localhost:8000

⸻

Windows

git clone https://github.com/hrshilll/Complain-Management-system.git
cd Complain-Management-system

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver


⸻

👥 User Roles & Permissions

Admin
	•	Manage all complaints
	•	Assign complaints to faculty
	•	Close complaints
	•	Manage users and categories
	•	Access Django Admin Panel (/admin)

Faculty
	•	View assigned complaints
	•	Update complaint status
	•	Add remarks
	•	Cannot close complaints

Student
	•	Submit new complaints
	•	Track their own complaints
	•	Provide feedback after resolution
	•	Cannot edit after submission

⸻

🔌 REST API Overview

Authentication via token-based login.

Get Token

POST /api/auth/token/

Key Endpoints

Method	Endpoint	Description
GET	/api/complaints/	List complaints
POST	/api/complaints/	Create complaint
GET	/api/complaints/{id}/	Complaint details
PATCH	/api/complaints/{id}/	Update complaint
POST	/api/complaints/{id}/assign/	Assign to faculty
GET	/api/stats/	System statistics


⸻

🧪 Testing

python manage.py test

Run specific tests:

python manage.py test complaints.tests


⸻

📁 Project Structure

Complain-Management-system/
├── config/          # Project settings
├── complaints/      # Core application
├── templates/       # HTML templates
├── static/          # CSS, JS
├── media/           # Uploaded files
├── scripts/         # Utility scripts
├── fixtures/        # Sample data
├── manage.py
├── requirements.txt
└── README.md


⸻

🔒 Security Measures
	•	Django authentication & permissions
	•	CSRF protection
	•	XSS-safe template rendering
	•	ORM-based SQL injection prevention
	•	File validation (type & size)

Security isn’t optional. It’s default.

⸻

🎯 Learning Outcomes
	•	Practical Django project structuring
	•	REST API design with authentication
	•	Role-based access control
	•	Database modeling & audit logging
	•	Realistic full-stack workflow design

⸻

🧩 Future Improvements
	•	Email & notification system
	•	Advanced analytics dashboard
	•	PostgreSQL support
	•	Docker deployment
	•	Production-ready caching

