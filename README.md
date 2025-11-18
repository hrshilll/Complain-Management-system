# Complaint Management System (CMS)

A full-featured Django web application for managing complaints in educational institutions. Supports multiple user roles (Admin, Faculty, Student) with role-based permissions, complete audit trails, file attachments, and a REST API.

## 🚀 Features

### Core Functionality
- **Multi-role System**: Admin, Faculty, and Student roles with different permissions
- **Complaint Management**: Create, assign, track, and resolve complaints
- **File Attachments**: Support for PDF, images, and documents (up to 10MB)
- **Status Tracking**: Pending → In Progress → Resolved → Closed workflow
- **Priority Management**: Low, Medium, High priority levels
- **Audit Trail**: Complete history of all complaint changes
- **Feedback System**: User feedback for resolved complaints
- **Auto-generated Complaint Numbers**: Format `CMP-YYYYMMDD-XXXXXX`

### Technical Features
- **REST API**: Django REST Framework with token authentication
- **Responsive UI**: Server-rendered Django templates with modern styling
- **File Security**: Safe file uploads with validation
- **Database**: SQLite for local development
- **Role-based Permissions**: Proper access control for all operations

## 📋 Requirements

- Python 3.11 or higher
- pip (Python package manager)
- SQLite (bundled with Python)

## 🛠️ Installation & Setup

### For macOS/Linux

#### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/CMS.git
cd CMS
```

#### 2. Create Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Set Up Environment Variables (Optional)
```bash
cp env.example .env
# Edit .env file if you want to customize settings
```

#### 5. Run Database Migrations
```bash
python manage.py migrate
```

#### 6. Create Superuser (Admin)
```bash
python manage.py createsuperuser
```
Follow the prompts to create an admin account.

#### 7. Load Sample Data (Optional)
```bash
python3 scripts/populate_sample_data.py
```

#### 8. Start Development Server
```bash
python manage.py runserver
```

Visit **http://localhost:8000** to access the application.

---

### For Windows

#### 1. Clone the Repository
```cmd
git clone https://github.com/yourusername/CMS.git
cd CMS
```

#### 2. Create Virtual Environment
```cmd
python -m venv .venv
.venv\Scripts\activate
```

#### 3. Install Dependencies
```cmd
pip install -r requirements.txt
```

#### 4. Set Up Environment Variables (Optional)
```cmd
copy env.example .env
:: Edit .env file if you want to customize settings
```

#### 5. Run Database Migrations
```cmd
python manage.py migrate
```

#### 6. Create Superuser (Admin)
```cmd
python manage.py createsuperuser
```
Follow the prompts to create an admin account.

#### 7. Load Sample Data (Optional)
```cmd
python scripts\populate_sample_data.py
```

#### 8. Start Development Server
```cmd
python manage.py runserver
```

Visit **http://localhost:8000** to access the application.

---

## 👥 User Roles & Permissions

### Admin
- Manage all complaints across the system
- Assign complaints to faculty members
- Close complaints
- Access Django admin panel (`/admin/`)
- Export reports
- Manage users and categories

### Faculty
- View complaints assigned to them
- Update complaint status
- Add remarks to complaints
- Cannot close complaints (only Admin can)

### Student
- Create new complaints
- View their own complaints
- Add feedback for resolved complaints
- Cannot edit complaints after submission

## 🔌 API Documentation

The system includes a RESTful API for programmatic access.

### Authentication

Get an authentication token:
```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/complaints/` | List complaints |
| POST | `/api/complaints/` | Create complaint |
| GET | `/api/complaints/{id}/` | Get complaint details |
| PATCH | `/api/complaints/{id}/` | Update complaint |
| POST | `/api/complaints/{id}/assign/` | Assign complaint to faculty |
| GET | `/api/categories/` | List categories |
| GET | `/api/feedback/` | List feedback |
| GET | `/api/stats/` | Get system statistics |
| POST | `/api/export/` | Export complaints (CSV/PDF) |

### Example: Create a Complaint
```bash
curl -X POST http://localhost:8000/api/complaints/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Network Issue",
    "description": "Internet connectivity problems in Lab 3",
    "category": 1,
    "priority": "HIGH"
  }'
```

### Example: Update Complaint Status
```bash
curl -X PATCH http://localhost:8000/api/complaints/CMP-20241201-000001/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "IN_PROGRESS"}'
```

## 🧪 Testing

Run tests with Django's test runner:
```bash
python manage.py test
```

Run specific test modules:
```bash
python manage.py test complaints.tests.test_models
```

## 🔧 Common Commands

### Development
```bash
# Start development server
python manage.py runserver

# Create migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files (for production)
python manage.py collectstatic

# Open Django shell
python manage.py shell
```

### Database
```bash
# Reset database (WARNING: Deletes all data)
rm db.sqlite3
python manage.py migrate

# Export data
python manage.py dumpdata > backup.json

# Import data
python manage.py loaddata backup.json
```

## 📁 Project Structure

```
CMS/
├── config/                 # Django configuration
│   ├── settings.py        # Main settings file
│   ├── urls.py            # Root URL configuration
│   ├── wsgi.py            # WSGI configuration
│   └── asgi.py            # ASGI configuration
├── complaints/            # Main application
│   ├── models.py          # Database models
│   ├── views.py           # View logic
│   ├── serializers.py     # API serializers
│   ├── forms.py           # Django forms
│   ├── urls.py            # App URL patterns
│   ├── admin.py           # Admin interface
│   └── templates/         # HTML templates
├── templates/             # Global templates
├── static/                # Static files (CSS, JS, images)
├── media/                 # User-uploaded files
├── scripts/               # Utility scripts
├── fixtures/              # Sample data
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
├── env.example            # Environment variables template
└── README.md              # This file
```

## 🗄️ Database Models

- **UserProfile**: Extended user model with role (Admin/Faculty/Student)
- **Category**: Complaint categories
- **Complaint**: Main complaint entity with status, priority, and attachments
- **ComplaintHistory**: Audit trail for all complaint changes
- **Feedback**: User satisfaction ratings for resolved complaints
- **Notification**: In-app notification system

## 🔒 Security Features

- Django's built-in authentication system
- Role-based access control
- CSRF protection on all forms
- XSS prevention with template auto-escaping
- SQL injection protection via ORM
- File upload validation (type and size)
- Secure file storage

## 📝 Development Guidelines

### Code Style
- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Write docstrings for functions and classes

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Commit changes
git add .
git commit -m "Description of changes"

# Push to remote
git push origin feature/your-feature-name
```

### Before Committing
- Test your changes
- Run migrations if models changed
- Update documentation if needed

## 🐛 Troubleshooting

### Virtual Environment Issues (Windows)
If you get a permission error when activating the virtual environment:
```cmd
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Port Already in Use
If port 8000 is already in use:
```bash
# Use a different port
python manage.py runserver 8080
```

### Migration Issues
```bash
# Reset migrations (WARNING: Development only)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
python manage.py makemigrations
python manage.py migrate
```

### Static Files Not Loading
```bash
python manage.py collectstatic --no-input
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

For issues and questions:
- **GitHub Issues**: [Create an issue](https://github.com/yourusername/CMS/issues)
- **Documentation**: Check this README and code comments
- **Email**: support@example.com

---

**Built with Django 4.2+ and Django REST Framework**



cd "/Users/harshilchauhan/Desktop/CMS-main"
source .venv/bin/activate
python3 manage.py runserver

cd "/Users/harshilchauhan/Desktop/CMS-main" && source .venv/bin/activate && python manage.py runserver 0.0.0.0:8000