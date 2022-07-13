import re
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .form import AnswerForm
import os
from .models import Essay
from .utils.ml_model import *


def home(request):
    return render(request, 'predictor/home.html')


def signupuser(request):
    if request.method == 'GET':
        return render(request, 'predictor/signupuser.html', {'form': UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('predictor')
            except IntegrityError:
                return render(request, 'predictor/signupuser.html',
                              {
                                'form': UserCreationForm(),
                                'error': "This username has already been taken. please choose another username"
                               }
                              )
        else:
            # password does not match
            return render(request, 'predictor/signupuser.html',
                          {
                              'form': UserCreationForm(),
                              'error': "Passwords don't match. please reenter"
                          }
                          )


def loginuser(request):
    if request.method == 'GET':
        return render(request, 'predictor/loginuser.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'predictor/loginuser.html',
                          {
                              'form': AuthenticationForm(),
                              'error': 'Username and password did not match'
                          }
                          )
        else:
            login(request, user)
            return redirect('predictor')


def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')


def predictor(request):
    if request.method == 'GET':
        form = AnswerForm()
        return render(request, 'predictor/predictor.html', {'form': form})
    else:
        # create a form instance and populate it with data from the request:
        form = AnswerForm(request.POST)

        if form.is_valid():
            content = [form.cleaned_data.get('answer')]

            inputs = tokenize(content)

            prediction = run_evaluation(inputs)

           # return redirect('result', {'result': content})
            essay = Essay.objects.create(
                content=content,
                score=prediction
            )
            return render(request, 'helper/result.html', {'result': prediction})


def result(request):
    return render(request, 'helper/result.html')

# Create your views here.
