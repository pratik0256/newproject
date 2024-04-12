from rest_framework import generics, status
from rest_framework.response import Response
from .models import CustomUser , Employee
from .serializers import CustomUserSerializer , EmployeeSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.models import User
from .serializers import UserSerializer
from .serializers import AdminLoginSerializer
from .serializers import EmployeeUpdateSerializer

class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

class TokenObtainView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        user = CustomUser.objects.filter(email=email).first()

        if user is None or not user.check_password(password):
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

class LoginView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        token = request.data.get('token')
        print(email)
        print(password)
        if token:
            try:
                token = RefreshToken(token)
                user_id = token.payload['user_id']
                user = CustomUser.objects.get(id=user_id)
                return Response({'message': 'Login successful', 'user': CustomUserSerializer(user).data})
            except Exception as e:
                return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if email and password:
            user = CustomUser.objects.filter(email=email).first()
            if user is None:
                return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
            if not user.check_password(password):
                return Response({'error': 'Invalid password'}, status=status.HTTP_401_UNAUTHORIZED)
            return Response({'message': 'Login successful', 'user': CustomUserSerializer(user).data})
        
        return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def create_employee(request):
    if request.method == 'POST':
        serializer = EmployeeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
# @permission_classes([IsAdminUser])
def create_admin_user(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.create_user(**serializer.validated_data)
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def admin_login(request):
    if request.method == 'POST':
        serializer = AdminLoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
from datetime import datetime
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Employee  # Assuming you have defined your Employee model
from .serializers import EmployeeSerializer  # Assuming you have defined your EmployeeSerializer
from rest_framework import status

@api_view(['GET'])
def get_all_employee_details(request):
    if request.method == 'GET':
        employees = Employee.objects.all()
        serializer = EmployeeSerializer(employees, many=True)

        employees_with_hours = {}

        for entry in serializer.data:  # Iterate over serialized data
            user_name = entry["user_name"]
            check_in_time = datetime.fromisoformat(entry["check_in"][:-1])  # Removing 'Z' at the end
            check_out_time = datetime.fromisoformat(entry["check_out"][:-1])  # Removing 'Z' at the end
            duration = (check_out_time - check_in_time).total_seconds() / 3600  # Convert seconds to hours

            if user_name in employees_with_hours:
                # If user name already exists, add the duration to existing working hours
                employees_with_hours[user_name]["working_hours"] += duration
            else:
                # If user name is encountered for the first time, create a new entry
                employees_with_hours[user_name] = {"working_hours": duration}

        print("Employees with their working hours:", employees_with_hours)

        response_data = {}

        for user_name, data in employees_with_hours.items():
            working_hours = data["working_hours"]
            if working_hours >= 8:
                response_data[user_name] = {
                    "working_hours": working_hours,
                    "attendance": "Full day"
                }
            else:
                response_data[user_name] = {
                    "working_hours": working_hours,
                    "attendance": "Half day"
                }

        return Response({"employees_with_hours": response_data}, status=status.HTTP_200_OK)


    
    
# views.py
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Employee

from rest_framework.permissions import IsAdminUser

@api_view(['GET'])
# @permission_classes([IsAdminUser])
def get_employee_details(request, employee_id):
    try:
        employee = Employee.objects.get(pk=employee_id)
    except Employee.DoesNotExist:
        return Response({'message': 'Employee not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = EmployeeSerializer(employee)
        return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['PATCH'])
# @permission_classes([IsAdminUser])
def update_employee_active_status(request, employee_id):
    try:
        employee = Employee.objects.get(pk=employee_id)
    except Employee.DoesNotExist:
        return Response({'message': 'Employee not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PATCH':
        serializer = EmployeeUpdateSerializer(employee, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



