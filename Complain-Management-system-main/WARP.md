# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Essential Commands

### Development Server
```bash
# Start development server (default port 8000)
python manage.py runserver

# Start on different port
python manage.py runserver 8080
```

### Database Operations
```bash
# Create new migrations after model changes
python manage.py makemigrations

# Apply migrations to database
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Open Django interactive shell
python manage.py shell
```

### Testing
```bash
# Run all tests
python manage.py test

# Run tests for specific app
python manage.py test complaints

# Run specific test file
python manage.py test complaints.tests.test_models
```

### Data Management
```bash
# Load sample data
python scripts/populate_sample_data.py

# Export database data
python manage.py dumpdata > backup.json

# Import database data
python manage.py loaddata backup.json
```

## Project Architecture

### High-Level Structure
This is a Django-based complaint management system with a REST API. The project follows Django's MVT (Model-View-Template) pattern with an additional API layer using Django REST Framework.

### Key Components

**Config (`config/`)**: Django project configuration
- `settings.py`: Central configuration (database, security, apps, middleware)
- `urls.py`: Root URL routing
- `wsgi.py`/`asgi.py`: WSGI/ASGI application entry points

**Main App (`complaints/`)**: Core business logic
- **Models** (`models.py`): 6 main models forming the data layer
  - `UserProfile`: Extends Django User with role (admin/faculty/student)
  - `Category`: Complaint categorization
  - `Complaint`: Main entity with auto-generated complaint numbers (CMP-YYYYMMDD-XXXXXX format)
  - `ComplaintHistory`: Audit trail for all changes
  - `Feedback`: User ratings for resolved complaints
  - `Notification`: In-app notification system

- **Views** (`views.py`): Contains both traditional Django views (for web UI) and API ViewSets (for REST API)
  - Role-based access control implemented at view level
  - Separate views for different user roles (admin/faculty/student)
  
- **Serializers** (`serializers.py`): REST API data transformation
  - Different serializers for list/detail/create/update operations
  
- **Forms** (`forms.py`): Django forms for web interface
  - Form validation and custom widgets
  
- **URLs** (`urls.py`): App-level routing for both web and API endpoints
  - Web URLs: `/complaints/`, `/dashboard/`, etc.
  - API URLs: `/api/complaints/`, `/api/categories/`, etc.

### Authentication & Authorization
- Uses Django's built-in authentication + custom UserProfile model
- Role-based permissions: admin > faculty > student
- Token authentication for API (Django REST Framework tokens)
- Session authentication for web interface

### Data Flow for Complaint Lifecycle
1. **Student** creates complaint → Status: PENDING
2. **Admin** assigns to faculty → History entry created
3. **Faculty** updates status to IN_PROGRESS → History entry created
4. **Faculty** marks as RESOLVED → `resolved_at` timestamp set
5. **Admin** closes complaint → Status: CLOSED
6. **Student** can add feedback after resolution

### File Upload Handling
- Files uploaded to `media/complaints/` with UUID-based names
- Validation: 10MB max, restricted extensions (pdf, jpg, jpeg, png, docx)
- Security: Files validated before storage, served via Django

### API Architecture
- RESTful API using Django REST Framework
- Token-based authentication
- Pagination enabled (20 items per page)
- Filtering, searching, and ordering supported
- Custom actions: `assign/` for complaint assignment

## Important Patterns & Conventions

### Model Patterns
- All models have `created_at` and `updated_at` timestamps (except when not applicable)
- Soft deletes not used (Django's CASCADE/PROTECT used for relationships)
- Complaint numbers auto-generated in `save()` method
- `ComplaintHistory` entries created via signals (see end of models.py)

### View Patterns
- Role checking: `user.profile.role` to determine permissions
- Permission errors raise `Http404` (not 403) to avoid information leakage
- Use `get_object_or_404` for object retrieval
- Complex queries use `select_related`/`prefetch_related` for performance

### URL Patterns
- Web interface uses descriptive slugs: `/complaints/new/`, `/complaints/<complaint_no>/`
- API uses RESTful conventions: `/api/complaints/`, `/api/complaints/{id}/`
- Complaint lookup by `complaint_no` (not database ID) for better UX

### Testing Approach
- Test directory: `complaints/tests/`
- Use Django's TestCase for model/view tests
- Test file naming: `test_models.py`, `test_views.py`, etc.
- Run migrations in test database automatically

## Common Development Tasks

### Adding a New Model Field
1. Add field to model in `complaints/models.py`
2. Run `python manage.py makemigrations`
3. Review the migration file
4. Run `python manage.py migrate`
5. Update serializers in `serializers.py` if API exposure needed
6. Update forms in `forms.py` if web form exposure needed

### Adding a New API Endpoint
1. Add method to ViewSet in `views.py` with `@action` decorator
2. Create/update serializer if needed
3. Test using curl or API client
4. Document in README if public-facing

### Modifying User Permissions
- Check role in view: `if request.user.profile.role == 'admin':`
- Use permission classes for API: `permission_classes = [IsAuthenticated]`
- Custom permissions can be added to `complaints/permissions.py` (create if needed)

### Database Schema Changes
- Always create migrations: `python manage.py makemigrations`
- Review generated migration before applying
- For production: test migration on copy of production data first
- Backward-incompatible changes require careful planning

## Technical Debt & Known Issues

### Areas for Improvement
- No Docker configuration (deployment complexity)
- Tests are limited (expand test coverage needed)
- No celery integration for async tasks (emails sent synchronously)
- No real-time notifications (consider WebSockets/channels)
- Static files served by Django in development (fine for dev, needs CDN for production)

### Configuration Notes
- SQLite for development (switch to PostgreSQL/MySQL for production)
- `DEBUG=True` in settings (must be False in production)
- SECRET_KEY hardcoded in settings.py (use environment variable in production)
- No CORS configuration (add if frontend is separate domain)

## Development Workflow

### Starting Work
```bash
# Activate virtual environment
source .venv/bin/activate  # Mac/Linux
.venv\Scripts\activate     # Windows

# Pull latest changes
git pull origin main

# Apply any new migrations
python manage.py migrate

# Start server
python manage.py runserver
```

### Before Committing
```bash
# Run tests
python manage.py test

# Check for migrations
python manage.py makemigrations --dry-run

# Verify no syntax errors
python manage.py check
```

### Code Style
- Follow PEP 8 (Django's style guide)
- Use Django's built-in functions (don't reinvent the wheel)
- Keep views thin, move logic to models or separate service layers
- Use Django ORM (avoid raw SQL unless absolutely necessary)

## Environment Variables
Key environment variables (see `env.example`):
- `DJANGO_SECRET_KEY`: Django secret key (required in production)
- `DEBUG`: Debug mode (True/False)
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `EMAIL_*`: Email configuration for notifications

## Quick Reference

### Default Admin Panel
- URL: `/admin/`
- Requires superuser account
- Manage all models, users, and data

### API Authentication
```bash
# Get token
curl -X POST http://localhost:8000/api/auth/token/ \
  -d "username=<user>&password=<pass>"

# Use token
curl -H "Authorization: Token <token>" \
  http://localhost:8000/api/complaints/
```

### Complaint Number Format
- Format: `CMP-YYYYMMDD-XXXXXX`
- Example: `CMP-20241110-000001`
- Sequential within each day
- Generated automatically on complaint creation
