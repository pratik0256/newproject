from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth.models import User
from .models import Employee
from rest_framework_simplejwt.tokens import RefreshToken


from rest_framework import serializers
from .models import CustomUser

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
        fields = ['id', 'user', 'user_name', 'check_in', 'check_out', 'is_active', 'is_working_from_home']

    def get_user_name(self, obj):
        return obj.user.employee_name  

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

