from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, employee_name, employee_code, password=None, is_active=None, is_admin=False, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, employee_name=employee_name, employee_code=employee_code, is_active=is_active, is_admin=is_admin, **extra_fields)
        if password:
            user.set_password(password)  # Set password using set_password method
        user.save(using=self._db)
        return user

    def create_superuser(self, email, employee_name, employee_code, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_admin') is not True:
            raise ValueError('Superuser must have is_admin=True.')

        return self.create_user(email, employee_name, employee_code, password=password, **extra_fields)


class CustomUser(AbstractBaseUser):
    email = models.EmailField(verbose_name='email', max_length=60, unique=True)
    employee_name = models.CharField(max_length=100)
    employee_code = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=None, null=True, blank=True)
    is_admin = models.BooleanField(default=False)

    objects = CustomUserManager()


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['employee_name', 'employee_code']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

class Employee(models.Model):
    # user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='employee_profile')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='employee_profile')
    check_in = models.DateTimeField(null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=None, null=True, blank=True)
    is_working_from_home = models.BooleanField(default=False)

    def __str__(self):
        try:
            return f"{self.user.employee_name}'s Employee Profile"
        except AttributeError:
            return f"{self.user.email}'s Employee Profile"
