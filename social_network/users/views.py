from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import User, FriendRequest
from .serializers import UserSerializer, FriendRequestSerializer
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
import re
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.db.models import Q
from django.core.cache import cache
import time


@login_required
def dashboard(request):
    received_requests = FriendRequest.objects.filter(receiver=request.user, status='pending')
    sent_requests = FriendRequest.objects.filter(sender=request.user)
    friends = User.objects.filter(sent_requests__receiver=request.user, sent_requests__status='accepted')

    context = {
        'received_requests': received_requests,
        'sent_requests': sent_requests,
        'friends': friends,
    }
    return render(request, 'dashboard.html', context)




@csrf_exempt
@login_required
def respond_to_friend_request(request):
    if request.method == 'POST':
        friend_request_id = request.POST.get('id')
        status_choice = request.POST.get('status')

        friend_request = get_object_or_404(FriendRequest, id=friend_request_id, receiver=request.user)

        if status_choice == 'accepted':
            friend_request.status = 'accepted'
            friend_request.save()
            messages.success(request, f"Friend request from {friend_request.sender.username} accepted.")

        elif status_choice == 'rejected':
            friend_request.delete()
            messages.info(request, f"Friend request from {friend_request.sender.username} rejected.")

        return redirect('dashboard')

class SignupView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return render(request, 'registration/signup.html')

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        username = request.data.get('username')
        name = request.data.get('name')
        password = request.data.get('password')

        if not re.match(r'^[A-Za-z0-9_]+$', username):
            return render(request, 'registration/signup.html', {'error': 'Username can only contain letters, numbers, and underscores.'})

        if not re.match(r'^[A-Za-z0-9 ]+$', name):
            return render(request, 'registration/signup.html', {'error': 'Name can only contain letters, numbers, and spaces.'})

        if User.objects.filter(email=email).exists():
            return render(request, 'registration/signup.html', {'error': 'Email already exists'})
        if User.objects.filter(username=username).exists():
            return render(request, 'registration/signup.html', {'error': 'Username already exists'})

        user = User.objects.create_user(email=email, username=username, name=name, password=password)
        user.save()

        return redirect('login')



class LoginView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return render(request, 'registration/login.html')

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'registration/login.html', {'error': 'Invalid credentials or user does not exist'})



class LogoutView(views.APIView):
    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect('home')



class UserSearchView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        if '@' in query:
            return User.objects.filter(email__iexact=query)
        return User.objects.filter(name__icontains=query)


@csrf_exempt
@login_required
def send_friend_request(request):
    if request.method == 'POST':
        receiver_username = request.POST.get('receiver')
        try:
            receiver = User.objects.get(username=receiver_username)
            sender = request.user
            now = time.time()
            cache_key = f'friend_request_{sender.id}'
            timestamps = cache.get(cache_key, [])

            timestamps = [timestamp for timestamp in timestamps if now - timestamp < 60]

            if len(timestamps) >= 3:
                messages.error(request, "You have exceeded the limit of 3 friend requests per minute.")
                return redirect('dashboard')

            timestamps.append(now)
            cache.set(cache_key, timestamps, timeout=60)
            if sender == receiver:
                messages.error(request, "You cannot send a friend request to yourself.")
                return redirect('dashboard')

            is_friend = FriendRequest.objects.filter(
                Q(sender=sender, receiver=receiver, status='accepted') |
                Q(sender=receiver, receiver=sender, status='accepted')
            ).exists()

            if is_friend:
                messages.error(request, "You are already friends with this user.")
                return redirect('dashboard')

            pending_request = FriendRequest.objects.filter(
                Q(sender=sender, receiver=receiver, status='pending') |
                Q(sender=receiver, receiver=sender, status='pending')
            ).exists()

            if pending_request:
                messages.error(request, "A friend request is already pending with this user.")
                return redirect('dashboard')

            FriendRequest.objects.create(sender=sender, receiver=receiver, status='pending')
            messages.success(request, "Friend request sent successfully.")
            return redirect('dashboard')

        except User.DoesNotExist:
            messages.error(request, "User does not exist.")
            return redirect('dashboard')


class AcceptRejectFriendRequestView(views.APIView):
    def post(self, request, *args, **kwargs):
        friend_request_id = request.data.get('id')
        status_choice = request.data.get('status')
        try:
            friend_request = get_object_or_404(FriendRequest, id=friend_request_id, receiver=request.user)
            friend_request.status = status_choice
            friend_request.save()
            return Response({"message": "Friend request updated"}, status=status.HTTP_200_OK)
        except FriendRequest.DoesNotExist:
            return Response({"message": "Friend request not found"}, status=status.HTTP_404_NOT_FOUND)


class ListFriendsView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(sent_requests__receiver=self.request.user, sent_requests__status='accepted')

class ListPendingRequestsView(generics.ListAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FriendRequest.objects.filter(receiver=self.request.user, status='pending')


@login_required
def friends_list(request):
    friends_as_sender = User.objects.filter(sent_requests__receiver=request.user, sent_requests__status='accepted')
    friends_as_receiver = User.objects.filter(received_requests__sender=request.user, received_requests__status='accepted')

    friends = friends_as_sender.union(friends_as_receiver)

    paginator = Paginator(friends, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'friends_list.html', {'page_obj': page_obj})

@login_required
def search_users(request):
    query = request.GET.get('q', '')
    search_results = []

    if query:
        if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', query):
            search_results = User.objects.filter(email__iexact=query)
        else:
            search_results = User.objects.filter(name__icontains=query)

    paginator = Paginator(search_results, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'search.html', {'page_obj': page_obj, 'search_results': page_obj.object_list, 'query': query})

@login_required
def search_page(request):
    return render(request, 'search.html')