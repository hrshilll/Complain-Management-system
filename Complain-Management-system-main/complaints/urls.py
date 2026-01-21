from django.urls import path,include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from . import views
# API Router
router = DefaultRouter()
router.register(r'complaints', views.ComplaintViewSet, basename='complaint')
router.register(r'feedback', views.FeedbackViewSet)
router.register(r'notifications', views.NotificationViewSet)

urlpatterns = [
    # Web URLs
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('complaints/', views.complaint_list, name='complaint_list'),
    path('complaints/new/', views.create_complaint, name='create_complaint'),
    path('complaints/<str:complaint_no>/', views.complaint_detail, name='complaint_detail'),
    path('complaints/<str:complaint_no>/edit/', views.update_complaint, name='update_complaint'),
    path('complaints/<str:complaint_no>/assign/', views.assign_complaint, name='assign_complaint'),
    path('complaints/<str:complaint_no>/feedback/', views.add_feedback, name='add_feedback'),
    path('complaints/<str:complaint_no>/update-status/', views.update_complaint_status, name='update_complaint_status'),
    path('register/', views.register, name='register'),
    path('faculty-directory/', views.faculty_directory, name='faculty_directory'),
    path('reports/', views.complaint_report, name='complaint_report'),
    path('reports/pdf/', views.complaint_report_pdf, name='complaint_report_pdf'),

    # Legacy URLs for backward compatibility
    path('my-complaints/', views.student_complaints_legacy, name='student_complaints'),
    path('faculty-dashboard/', views.faculty_dashboard_legacy, name='faculty_dashboard'),
    path('create/', views.create_complaint_legacy, name='create_complaint_legacy'),
    path('update/<int:complaint_id>/', views.update_status_legacy, name='update_status'),
    path('faculty/', views.faculty_dashboard_legacy, name='Faculty'),
    path('complaints/<str:complaint_no>/assign/',views.assign_complaint,name='assign_complaint'),

    # API URLs
    path('api/', include(router.urls)),
    path('api/auth/token/', obtain_auth_token, name='api_token_auth'),
    path('api/stats/', views.complaint_stats, name='complaint_stats'),
    path('api/export/', views.export_complaints, name='export_complaints'),
    path('api/schema/', include('rest_framework.urls')),
    path('ajax/load-subcategories/', views.load_subcategories, name='ajax_load_subcategories'),


]