from rest_framework import generics, status
from rest_framework.response import Response
from .models import CustomUser, Employee
from .serializers import CustomUserSerializer, EmployeeSerializer, UserSerializer, AdminLoginSerializer, EmployeeUpdateSerializer, UserWithEmployeesSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.models import User
from datetime import datetime, timedelta, date
from collections import defaultdict
from django.utils import timezone

##________Excel___________
import pandas as pd
from django.http import HttpResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from io import BytesIO



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

        if email and password:
            user = CustomUser.objects.filter(email=email).first()
            if user is None:
                return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
            if not user.check_password(password):
                return Response({'error': 'Invalid password'}, status=status.HTTP_401_UNAUTHORIZED)

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            return Response({
                'message': 'Login successful',
                'user': CustomUserSerializer(user).data,
                'refresh': str(refresh),
                'access_token': access_token
            })

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
    

@api_view(['GET'])
def get_employee_details(request):
    user = request.GET.get('user')
    print(user)
    try:
        if user:
            employee = Employee.objects.filter(user=user)
            print(employee)
        else:
            employee = Employee.objects.get(user=user)
    except Employee.DoesNotExist:
        return Response({'message': 'Employee not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = EmployeeSerializer(employee, many = True)
        return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['PATCH'])
def update_employee_active_status(request):
    user = request.query_params.get('user')
    try:
        employee = Employee.objects.filter(user=user).first()
    except Employee.DoesNotExist:
        return Response({'message': 'Employee not found.'}, status=status.HTTP_404_NOT_FOUND)

    if not employee:
        return Response({'message': 'Employee not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PATCH':
        serializer = EmployeeUpdateSerializer(employee, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


@method_decorator(csrf_exempt, name='dispatch')
class DownloadAttendance(View):
    def get(self, request):
        # Retrieve attendance data from your database
        employees = Employee.objects.all()
        
        # Create a dictionary to store attendance data organized by user and date
        user_data = {}
        for employee in employees:
            user = employee.user.employee_name
            date = employee.check_in.date().strftime('%d/%m/%Y')
            # Calculate the duration between check-in and check-out
            duration = employee.check_out - employee.check_in
            # Determine status based on duration
            if duration < timedelta(hours=8):
                status = 'Half Day'
            else:
                status = 'Present'
            if user not in user_data:
                user_data[user] = {}
            user_data[user][date] = status
        
        # Convert the dictionary to DataFrame
        df = pd.DataFrame(user_data)

        # Transpose the DataFrame to have users as rows and dates as columns
        df = df.transpose()

        # Mark all dates other than "Half Day" and "Present" as "Absent"
        for user in df.index:
            for column in df.columns:
                if pd.isna(df.loc[user, column]):
                    df.loc[user, column] = 'Absent'

        # Create BytesIO object to store Excel file as bytes
        output = BytesIO()

        # Create Excel writer object
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # Write DataFrame to Excel
            df.to_excel(writer, sheet_name='Attendance')

        # Set the BytesIO object's cursor to the beginning
        output.seek(0)

        # Create HttpResponse object with the Excel file bytes
        response = HttpResponse(output.getvalue(), content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=attendance.xlsx'
        
        return response
    


class UserWithEmployeesList(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserWithEmployeesSerializer
