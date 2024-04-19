from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

from datetime import timedelta
from collections import defaultdict
from .models import CustomUser, Employee

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'employee_name', 'employee_code', 'password' ,  'is_admin')

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user

    def validate_email(self, value):
        """
        Check if the email is unique.
        """
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

 
class EmployeeSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = [ 'id', 'user', 'user_name', 'check_in', 'check_out', 'is_active', 'is_working_from_home']

    def get_user_name(self, obj):
        return obj.user.employee_name  
    
    def create(self, validated_data):
        return Employee.objects.create(**validated_data)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        
class AdminLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username', None)
        password = data.get('password', None)

        if username is None or password is None:
            raise serializers.ValidationError(
                'Both username and password are required to log in as an admin.'
            )

        user = User.objects.filter(username=username).first()

        if user is None:
            raise serializers.ValidationError('User with this username does not exist.')

        if not user.is_staff:
            raise serializers.ValidationError('Only admin users can log in through this endpoint.')

        if not user.check_password(password):
            raise serializers.ValidationError('Incorrect password.')

        return {
            'username': user.username,
            'token': str(RefreshToken.for_user(user).access_token),
        }


class EmployeeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['is_active']  # Specify the fields that can be updated

    def update(self, instance, validated_data):
        """
        Perform the update operation, allowing partial updates.
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class EmployeeProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'check_in', 'check_out', 'is_active', 'is_working_from_home', 'created_date']

class UserWithEmployeesSerializer(serializers.ModelSerializer):
    employee_profile = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'employee_name', 'employee_code', 'employee_profile']

    def get_employee_profile(self, obj):
        employee_profiles = defaultdict(float)

        # Group employee profiles by created_date and calculate total working hours for each date
        for employee in obj.employee_profile.all():
            if employee.check_in and employee.check_out:
                duration = employee.check_out - employee.check_in
                total_hours = duration.total_seconds() / 3600  # Convert seconds to hours
            else:
                total_hours = 0

            # Determine if it's a full day, half day, or absent
            if total_hours >= 8:
                status = "full day"
            elif total_hours > 0:
                status = "half day"
            else:
                status = "absent"

            employee_profiles[employee.created_date] = {
                'total_working_hours': total_hours,
                'status': status
            }

        # Convert employee_profiles to list of dictionaries
        result = [{'created_date': created_date, **details}
                  for created_date, details in employee_profiles.items()]

        return result
