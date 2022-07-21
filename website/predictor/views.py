import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .form import AnswerForm
import os
from .models import Essay
from .utils.ml_model import *
from .utils.process_text import *


def home(request):
    essay_list = Essay.objects.filter(user_id=request.user.id).order_by('id').reverse()[:10]
    context = {
        'essays': essay_list,
    }
    return render(request, 'predictor/home.html', context)


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
            return redirect('home')


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

            if request.user != None:
                current_user = request.user.id
           # return redirect('result', {'result': content})
            essay = Essay.objects.create(
                content=content,
                score=prediction,
                user_id=current_user,
            )
            return redirect('result', essay_id=essay.id)


def result(request, essay_id):
    essay = Essay.objects.get(id=essay_id)
    essay_text = essay_content(essay.content)
    essay_band = convert_score(essay.score)
    context = {
        "submission": essay_text,
        "band": essay_band,
        "score": essay.score
        #"score": 1
    }
    return render(request, 'helper/result.html', context)

# Create your views here.
