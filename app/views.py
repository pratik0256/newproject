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
from datetime import datetime

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
    


from .serializers import EmployeeSerializer
from datetime import datetime, date
from collections import defaultdict
from rest_framework.response import Response
from rest_framework import status
from .models import Employee
from .serializers import EmployeeSerializer

# @api_view(['GET'])
# def get_all_employee_details(request):
#     if request.method == 'GET':
#         # Fetch all employees
#         employees = Employee.objects.all()
#         serializer = EmployeeSerializer(employees, many=True)
#         employees_with_hours = defaultdict(lambda: defaultdict(float))

#         # Initialize a set to store registered users
#         registered_users = set(entry["user_name"] for entry in serializer.data)

#         # Iterate over each employee to calculate working hours
#         for entry in serializer.data: 
#             user_name = entry["user_name"]
#             check_in = entry.get("check_in", None)
#             check_out = entry.get("check_out", None)

#             if user_name in registered_users:
#                 if check_in and check_out:  # If both check-in and check-out data exist
#                     check_in_time = datetime.fromisoformat(check_in[:-1])
#                     check_out_time = datetime.fromisoformat(check_out[:-1])
#                     date_key = check_in_time.date()

#                     duration = (check_out_time - check_in_time).total_seconds() / 3600
#                     employees_with_hours[user_name][date_key] += duration
#                 else:
#                     # If either check-in or check-out data is missing, mark the employee as absent
#                     date_key = datetime.now().date()  # Use current date as key
#                     employees_with_hours[user_name][date_key] = 0

#         # Fetch all users from CustomUser model
#         users = CustomUser.objects.all()

#         # Iterate over each user to check if they are registered as an employee
#         for user in users:
#             user_name = user.name  # Assuming 'name' is the attribute in CustomUser model
#             if user_name not in employees_with_hours:
#         # If the user is not present in the Employee model, mark them as absent
#                 employees_with_hours[user_name] = {datetime.now().date(): 0}

#         # Prepare response data
#         response_data = {}
#         for user_name, date_hours in employees_with_hours.items():
#             user_data = []
#             for date_key, working_hours in date_hours.items():
#                 if working_hours == 0:
#                     user_data.append({
#                         "date": date_key.strftime("%Y-%m-%d"),
#                         "working_hours": working_hours,
#                         "attendance": "Absent",
#                     })
#                 elif working_hours >= 8:
#                     user_data.append({
#                         "date": date_key.strftime("%Y-%m-%d"),
#                         "working_hours": working_hours,
#                         "attendance": "Full day",
#                     })
#                 elif working_hours < 8:
#                     user_data.append({
#                         "date": date_key.strftime("%Y-%m-%d"),
#                         "working_hours": working_hours,
#                         "attendance": "Half day",
#                     })
#             response_data[user_name] = user_data

#         return Response(response_data, status=status.HTTP_200_OK)



    
# views.py
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Employee

from rest_framework.permissions import IsAdminUser

from django.contrib.auth.models import User

# @api_view(['GET'])
# def get_employee_details(request, employee_id=None):
#     user = request.user
#     try:
#         if employee_id:
#             user = Employee.objects.get(pk=employee_id).user.id
#             employee = Employee.objects.filter(user=user)
#             print(employee)
#         else:
#             employee = Employee.objects.get(user=user)
#     except Employee.DoesNotExist:
#         return Response({'message': 'Employee not found.'}, status=status.HTTP_404_NOT_FOUND)

#     if request.method == 'GET':
#         serializer = EmployeeSerializer(employee, many = True)
#         return Response(serializer.data, status=status.HTTP_200_OK)

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
    
from datetime import timedelta, date
from collections import defaultdict
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from .models import Employee
from .serializers import EmployeeSerializer

def get_all_checkin_checkout_times():
    employees_times = Employee.objects.all().values('user__employee_name', 'check_in', 'check_out')
    return employees_times

def filter_weekday_dates(employees_times, weekday_dates):
    weekday_dates_set = set(weekday_dates)
    filtered_times = [
        entry for entry in employees_times if entry['check_in'].date() in weekday_dates_set
    ]
    return filtered_times

def get_weekday_dates(start_date, end_date):
    all_dates = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]
    filtered_dates = [d for d in all_dates if d.weekday() < 5]
    return filtered_dates

@api_view(['GET'])
def get_all_employee_details(request):
    if request.method == 'GET':
        # Retrieve all employees
        employees = Employee.objects.all()
        #print('employees------------',employees)
        users = CustomUser.objects.all()
       # print('users---------', users)
        for user in users:
            print('user-------------------',user)
            employees = Employee.objects.filter(user=user)
            print('employees--------------------------',employees)
        serializer = EmployeeSerializer(employees, many=True)
        
        # Initialize response data
        response_data = defaultdict(list)

        # Get all check-in and check-out times
        employees_times = get_all_checkin_checkout_times()
        
        # Get weekday dates
        weekday_dates = get_weekday_dates(min([entry['check_in'] for entry in employees_times]), 
                                           max([entry['check_in'] for entry in employees_times]))
        
        # Filter check-in and check-out times for weekday dates
        filtered_times = filter_weekday_dates(employees_times, weekday_dates)
        
        # Calculate working hours for each employee
        employees_with_hours = defaultdict(lambda: defaultdict(float))
        for entry in serializer.data:
            user_name = entry["user_name"]
            check_in = entry.get("check_in", None)
            check_out = entry.get("check_out", None)
            if check_in and check_out:
                check_in_time = datetime.fromisoformat(check_in[:-1])
                check_out_time = datetime.fromisoformat(check_out[:-1])
                date_key = check_in_time.date()
                duration = (check_out_time - check_in_time).total_seconds() / 3600
                employees_with_hours[user_name][date_key] += duration
        
        # Retrieve email addresses from the database
        email_addresses = [entry['email'] for entry in CustomUser.objects.all().values('email')]
        
        # Generate response data for each user
        for email in email_addresses:
            user_data = []
            for date_key in weekday_dates:
                working_hours = employees_with_hours.get(email, {}).get(date_key, 0)
                if working_hours == 0:
                    user_data.append({
                        "date": date_key.strftime("%Y-%m-%d"),
                        "working_hours": working_hours,
                        "attendance": "Absent",
                    })
            response_data[email] = user_data
        response_data1 = defaultdict(list)
        
        # Include present data for each user
        for user_name, date_hours in employees_with_hours.items():
            user_data = []
            for date_key, working_hours in date_hours.items():
                if working_hours != 0:
                    attendance = "Full day" if working_hours >= 8 else "Half day"
                    user_data.append({
                        "date": date_key.strftime("%Y-%m-%d"),
                        "working_hours": round(working_hours, 2),
                        "attendance": attendance,
                    })
            response_data1[email] += user_data 
        # print(response_data,"response----------------------------")
        # print(response_data1,"responsedata1----------------------------")
        
# Create a new dictionary to store the merged values
    merged_response = defaultdict(list)

# Add values from response to merged_response
    for key, value in response_data.items():
        merged_response[key].extend(value)

# Add values from response1 to merged_response
    for key, value in response_data1.items():
        merged_response[key].extend(value)

# Get the keys that are only present in response or response1
    unique_keys_response = set(response_data.keys())
    unique_keys_response1 = set(response_data1.keys())
    unique_keys = unique_keys_response.symmetric_difference(unique_keys_response1)

# Add values for keys that are only present in response or response1 to merged_response
    for key in unique_keys:
        if key in response_data:
            merged_response[key].extend(response_data[key])
        elif key in response_data1:
            merged_response[key].extend(response_data1[key])

    #print(dict(merged_response))
        
        
    return Response(merged_response, status=status.HTTP_200_OK)