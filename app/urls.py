from django.urls import path
from .views import RegisterView ,LoginView , TokenObtainView , create_employee , create_admin_user , admin_login , get_all_employee_details , update_employee_active_status  , get_employee_details
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'), 
    path('token/', TokenObtainView.as_view(),name='TokenObtainView'), 
    path('employees/', create_employee, name='create_employee'),
    path('admin/users/', create_admin_user, name='create_admin_user'),
    path('admin/login/', admin_login, name='admin_login'),
    path('admin/employees/', get_all_employee_details, name='get_all_employee_details'),
    path('admin/employees/update_active_status/', update_employee_active_status, name='update_employee_active_status'),
    path('admin/employee/', get_employee_details, name='get_employee_details'),
    
]

