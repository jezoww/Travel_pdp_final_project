from django.contrib.auth import login
from django.http import HttpResponse
from django.shortcuts import render

from django.shortcuts import render
from django.views import View
from rest_framework_simplejwt.authentication import JWTAuthentication

from django.shortcuts import render

from user.models import User


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        email = request.POST.get('email')
        user = User.objects.get(email=email)
        print(user)
        login(request, user)
        print("Login")
        return render(request, 'login.html')


from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def chat_view(request, user2_id):
    return render(request, "index.html", {"user2_id": user2_id})
