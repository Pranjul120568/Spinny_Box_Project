from django.shortcuts import render
from rest_framework import viewsets
from .serializers import user_serializers, box_serializers, room_serializers, box_not_staff_serializers
from .models import User, room, box
import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import jwt
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.hashers import check_password
from .authentication import is_logged_in
from .dates import get_week
from .filterboxes import filter_boxes

# Create your views here.
TOTAL_ROOM_AREA = 1000
TOTAL_ROOM_VOLUME = 10000
MAXIMUM_BOXES_IN_A_WEEK = 50
MAXIMUM_BOXES_FOR_A_USER_IN_A_WEEK = 5


# class UserModelViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = user_serializers

class getbox(APIView):
    def post(self, request, pk=None, format=None):
        logged_in = is_logged_in(request)
        if not logged_in:
            raise AuthenticationFailed('Unauthenticated!')
        box_id = pk
        box_data = box.objects.get(id=box_id)
        serializer = box_serializers(box_data)
        return Response(serializer.data)


class box_request(APIView):
    def get(self, request, format=None):
        queries = request.GET.dict()
        logged_in = is_logged_in(request)
        if not logged_in:
            raise AuthenticationFailed('Unauthenticated!')
        token = request.headers['Authorization'][7:]
        if token is None:
            token = request.COOKIES.get('jwt')
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        user_id = payload['id']
        queryset = filter_boxes(queries=queries)
        if not payload['is_staff']:
            queryset = queryset.values('id', 'length', 'breadth', 'height',
                                       'area', 'volume')
            serializer = box_not_staff_serializers(queryset, many=True)
        else:
            serializer = box_serializers(queryset, many=True, partial=True)
        return Response(serializer.data)


class add_request(APIView):
    def post(self, request, format=None):
        logged_in = is_logged_in(request)
        if not logged_in:
            raise AuthenticationFailed('Unauthenticated!')

        token = request.headers['Authorization'][7:]
        if token is None:
            token = request.COOKIES.get('jwt')
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        user_id = payload['id']
        week = get_week()
        if not payload['is_staff']:
            return Response({'msg': 'User is not staff'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=user_id)
            room_data = room.objects.get(id=1)
            boxes_by_user = box.objects.filter(
                creator=user.email, current_week=week)
            boxes_in_week = box.objects.filter(current_week=week)
            length = request.data.get('length')
            breadth = request.data.get('breadth')
            height = request.data.get('height')
            box_area = length * breadth
            box_volume = length * breadth * height
            average_area = ((room_data.average_area * room_data.total_boxes) +
                            box_area) / (room_data.total_boxes+1)
            average_volume = ((room_data.average_volume * room_data.total_boxes) +
                              box_volume) / (room_data.total_boxes+1)

            average_area = int(average_area)
            average_volume = int(average_volume)
        except:
            return Response({'msg': 'Could not fetch'}, status=status.HTTP_400_BAD_REQUEST)
        if not average_area < TOTAL_ROOM_AREA and average_volume < TOTAL_ROOM_VOLUME:
            return Response({'msg': "Room volume or area is full remove some boxes"}, status=status.HTTP_400_BAD_REQUEST)
        if len(boxes_by_user) == MAXIMUM_BOXES_FOR_A_USER_IN_A_WEEK:
            return Response({'msg': "User cannot create more boxes"}, status=status.HTTP_400_BAD_REQUEST)
        if len(boxes_in_week) == MAXIMUM_BOXES_IN_A_WEEK:
            return Response({'msg': "Room can't put more boxes in this week"}, status=status.HTTP_400_BAD_REQUEST)
        # save the box in api and also update the room api
        box_data = {'length': length, 'breadth': breadth, 'height': height,
                    'area': box_area, 'volume': box_volume, 'creator': user.email, 'last_updated_by': user.username, 'last_updated_on': datetime.date.today(), 'created_on': datetime.date.today(), 'current_week': week}
        updated_room_data = {'average_area': average_area,
                             'average_volume': average_volume, 'total_boxes': room_data.total_boxes+1}

        box_serializer = box_serializers(data=box_data)
        room_serializer = room_serializers(
            room_data, data=updated_room_data, partial=True)
        if box_serializer.is_valid() and room_serializer.is_valid():
            try:
                box_serializer.save()
                room_serializer.save()
            except:
                return Response({'msg': " try again!!"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'msg': "Server Error!!"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'msg': "Box saved Successfully!!", "data": box_data}, status=status.HTTP_201_CREATED)


class update_request(APIView):
    def put(self, request, format=None):
        logged_in = is_logged_in(request)
        if not logged_in:
            raise AuthenticationFailed('Unauthenticated!')

        token = request.headers['Authorization'][7:]
        if token is None:
            token = request.COOKIES.get('jwt')
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        user_id = payload['id']
        week = get_week()
        if not payload['is_staff']:
            return Response({'msg': 'User is not staff'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            box_id = request.data.get('id')
        except:
            return Response({'msg': 'No id attached'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=user_id)
            room_data = room.objects.get(id=1)
            box_data = box.objects.get(id=box_id)
            length = box_data.length
            breadth = box_data.breadth
            height = box_data.height
            box_area = length * breadth
            box_volume = length * breadth * height
            average_area = ((room_data.average_area * room_data.total_boxes) -
                            box_area) / (room_data.total_boxes-1)
            average_volume = ((room_data.average_volume * room_data.total_boxes) -
                              box_volume) / (room_data.total_boxes-1)
            boxes_by_user = box.objects.filter(
                creator=user.email, current_week=week)
            boxes_in_week = box.objects.filter(current_week=week)
            if request.data.get('length'):
                length = request.data.get('length')
            if request.data.get('breadth'):
                breadth = request.data.get('breadth')
            if request.data.get('height'):
                height = request.data.get('height')
            box_area = length * breadth
            box_volume = length * breadth * height
            average_area = ((room_data.average_area * room_data.total_boxes) +
                            box_area) / (room_data.total_boxes+1)
            average_volume = ((room_data.average_volume * room_data.total_boxes) +
                              box_volume) / (room_data.total_boxes+1)

            average_area = int(average_area)
            average_volume = int(average_volume)
        except:
            return Response({'msg': 'Could not fetch'}, status=status.HTTP_400_BAD_REQUEST)
        # save the box in api and also update the room api
        updated_box_data = {'length': length, 'breadth': breadth, 'height': height,
                            'area': box_area, 'volume': box_volume, 'last_updated_by': user.username, 'last_updated_on': datetime.date.today()}
        updated_room_data = {'average_area': average_area,
                             'average_volume': average_volume}

        box_serializer = box_serializers(
            box_data, data=updated_box_data, partial=True)
        room_serializer = room_serializers(
            room_data, data=updated_room_data, partial=True)
        if box_serializer.is_valid() and room_serializer.is_valid():
            try:
                box_serializer.save()
                room_serializer.save()
            except:
                return Response({'msg': "Please try again!!"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'msg': "Server Error!!"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'msg': "Box updated Successfully!!", "data": updated_box_data}, status=status.HTTP_201_CREATED)


class delete_request(APIView):
    def delete(self, request, id=None):
        logged_in = is_logged_in(request)
        if not logged_in:
            raise AuthenticationFailed('Unauthenticated!')
        print(request.data)
        try:
            box_id = id
        except:
            return Response({'msg': 'No id attached'}, status=status.HTTP_400_BAD_REQUEST)
        token = request.headers['Authorization'][7:]
        if token is None:
            token = request.COOKIES.get('jwt')
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        user_id = payload['id']
        week = get_week()
        if not payload['is_staff']:
            return Response({'msg': 'User is not staff'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=user_id)
            room_data = room.objects.get(id=1)
            box_data = box.objects.get(id=box_id)
            length = box_data.length
            breadth = box_data.breadth
            height = box_data.height
            box_area = length * breadth
            box_volume = length * breadth * height
            average_area = ((room_data.average_area * room_data.total_boxes) -
                            box_area) / (room_data.total_boxes-1)
            average_volume = ((room_data.average_volume * room_data.total_boxes) -
                              box_volume) / (room_data.total_boxes-1)
            average_area = int(average_area)
            average_volume = int(average_volume)
        except:
            return Response({'msg': 'Could not delete'}, status=status.HTTP_400_BAD_REQUEST)
        updated_room_data = {'average_area': average_area,
                             'average_volume': average_volume, 'total_boxes': room_data.total_boxes-1}
        if user.email != box_data.creator:
            return Response({'msg': 'Only creator can delete the box'}, status=status.HTTP_400_BAD_REQUEST)
        room_serializer = room_serializers(
            room_data, data=updated_room_data, partial=True)
        if room_serializer.is_valid():
            try:
                room_serializer.save()
                box_data.delete()
            except:
                return Response({'msg': "Please try again!!"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'msg': "Server Error!!"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'msg': "Box deleted Successfully!!"}, status=status.HTTP_201_CREATED)


class register_user(APIView):
    def post(self, request, format=None):
        password = request.data['password']
        confirm_password = request.data['confirm_password']
        if password != confirm_password or confirm_password is None:
            return Response({'msg': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = user_serializers(data=request.data)

        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors)
        try:
            payload = {
                'id': request.data['email'],
                'is_staff': False,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
                'iat': datetime.datetime.utcnow()
            }
            token = jwt.encode(payload, 'secret',
                               algorithm='HS256')
            # .decode('utf-8')
            response = Response()
            response.set_cookie(key='jwt', value=token, httponly=True)
            response.data = {
                'jwt': token,
                'email': request.data['email'],
                'is_staff': False

            }
            return response
        except:
            return Response({'msg': 'User data not valid!'}, status=status.HTTP_400_BAD_REQUEST)


class get_users(APIView):
    def get(self, request, format=None):
        logged_in = is_logged_in(request)
        if logged_in:
            try:
                user = User.objects.all()
                serializer = user_serializers(user, many=True)
                return Response(serializer.data)
            except:
                return Response({'msg': 'Could not fetch'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            raise AuthenticationFailed('Unauthenticated!')


class getuser(APIView):
    def get(self, request, format=None):
        logged_in = is_logged_in(request)
        if logged_in:
            try:
                token = request.headers['Authorization'][7:]
                if token is None:
                    token = request.COOKIES.get('jwt')
                payload = jwt.decode(token, 'secret', algorithms=['HS256'])
                user_id = payload['id']
                user = User.objects.get(email=user_id)
                serializer = user_serializers(user)
                return Response(serializer.data)
            except:
                return Response({'msg': 'Could not fetch'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            raise AuthenticationFailed('Unauthenticated!')


class login_user(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()
        if user is None:
            raise AuthenticationFailed('User not found!')

        if password != user.password:
            raise AuthenticationFailed('Incorrect password!')

        payload = {
            'id': user.email,
            'is_staff': user.is_staff,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret',
                           algorithm='HS256')
        # .decode('utf-8')

        response = Response()

        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'jwt': token,
            'is_staff': user.is_staff,
            'email': user.email

        }
        return response


class logout_user(APIView):
    def post(self, request):
        response = Response()
        token = request.headers['Authorization'][7:]
        if token is None:
            token = request.COOKIES.get('jwt')
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        # print(payload)
        response.delete_cookie('jwt')
        response.data = {
            'message': 'success'
        }
        return response
