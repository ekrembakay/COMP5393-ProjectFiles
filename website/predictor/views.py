import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .form import AnswerForm
import os
from .models import Essay
from django.conf import settings
from transformers import BertTokenizer, BertForSequenceClassification
import torch

path_to_model = os.path.join(settings.BASE_DIR, 'static/model/')
model_file = os.path.join(path_to_model, 'model.model')
loaded_model = torch.load(model_file, map_location=torch.device('cpu'))

def get_device():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    return device

def get_model():

    model = BertForSequenceClassification.from_pretrained("bert-base-uncased",
                                                          num_labels=3,
                                                          output_attentions=False,
                                                          output_hidden_states=False)

    return model

def tokenize(text):
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased', do_lower_case=True)
    encoded_data = tokenizer.batch_encode_plus(
        text,
        add_special_tokens=True,
        return_attention_mask=True,
        padding='max_length',
        max_length=318,
        truncation=True,
        return_tensors='pt'
    )

    return encoded_data

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

            try:
                data = tokenize(content)

                model = get_model()
                # model.to(get_device())
                model.load_state_dict(loaded_model)

                model.eval()

                with torch.no_grad():
                    logits = model(**data).logits

                prediction = logits.argmax().item()

                if request.user != None:
                    current_user = request.user.id
                # return redirect('result', {'result': content})
                essay = Essay.objects.create(
                    content=content,
                    score=prediction,
                    user_id=current_user,
                )
                return redirect('result', essay_id=essay.id)

            except ValueError as ve:
                model_prediction = {
                    'error_code' : '-1',
                    "info": str(ve)
                }
                return render(request, 'predictor/predictor.html', model_prediction)




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