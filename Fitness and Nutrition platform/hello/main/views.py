from django.shortcuts import render, redirect, HttpResponse
from .models import Client, Trainer, Owner, Discussion, Plan, Plan_Content, Rating, Appointment, Payment, wPlan_Content, wPlan
from django.contrib.auth.models import User, auth
from django.contrib import messages
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from datetime import datetime
from .forms import CustomForm
from .forms import BMIForm
from .models import BMIRecord
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string, get_template 
import logging

def homepage(request):
    return render(request, 'home.html')

def clientLogin(request):
    if request.method == 'POST':
        client_usrname = request.POST['clientusrname']
        password = request.POST['password']
        user = auth.authenticate(username=client_usrname, password=password)
        if user is not None and Client.objects.filter(client_usrname=client_usrname).exists():
            auth.login(request, user)
            return redirect('clientProfile')
        else:
            messages.info(request, 'Invalid Credentials')
            return redirect('clientLogin')
    return render(request, 'client_login.html')

def trainerLogin(request):
    if request.method == 'POST':
        print(request.POST)  # Add this line to debug
        try:
            user_name = request.POST['username']
            password = request.POST['password']
        except KeyError as e:
            print(f"KeyError: {e}")  # This will help you identify if the key is missing
            messages.error(request, 'Invalid form submission')
            return redirect('trainerLogin')

        user = auth.authenticate(username=user_name, password=password)
        if user is not None and Trainer.objects.filter(user=user).exists():
            auth.login(request, user)
            return redirect('trainerProfile')
        else:
            messages.info(request, 'Invalid Credentials')
            return redirect('trainerLogin')
    return render(request, 'trainer_login.html')


def ownerLogin(request):
    if request.method == 'POST':
        user_name = request.POST['clientusrname']
        #user_name = request.POST.get('owner_usrname', "error")
        password = request.POST['password']
        print(user_name)
        print(password)
        user = auth.authenticate(username=user_name, password=password)
        print('done')
        print(user)
        if user is not None and Owner.objects.filter(user=user).exists():
            print('hello')
            auth.login(request, user)
            return redirect('ownerProfile')
        else:
            messages.info(request, 'Invalid Credentials')
            return redirect('ownerLogin')

    return render(request, 'owner_login.html')

def clientRegister(request):
    if request.method == 'POST':
        client_usrname = request.POST['clientusrname']
        email = request.POST['email']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(username=client_usrname).exists():
                messages.info(request, 'Username Taken')
                return redirect('clientRegister')
            elif User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return redirect('clientRegister')
            else:
                user = User.objects.create_user(
                    username=client_usrname,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                user.save()

                # Create the Client instance
                client = Client.objects.create(
                    user=user,
                    client_usrname=client_usrname,
                    email=email,
                    # Optionally add first_name and last_name if needed
                    first_name=first_name,
                    last_name=last_name
                )
                client.save()
                return redirect('clientLogin')
        else:
            messages.info(request, 'Password not matching')
            return redirect('clientRegister')  
    return render(request, 'client_reg.html')

@login_required(login_url='clientLogin')
def clientProfile(request):
    if Client.objects.filter(user=request.user).exists():
        user = request.user
        obj = User.objects.get(username=user)

        if Client.objects.filter(user=obj).exists():
            obj = Client.objects.get(user=obj)
            return render(request, 'client_profile.html', {'user': obj, "client": "client"})
        
        return render(request, 'client_profile.html', {'user': obj})
    else:
        # return redirect('clientLogin')
        return render(request, 'client_profile.html', {"client": "client"})
    

@login_required(login_url='trainerLogin')
def trainerProfile(request):
    if Trainer.objects.filter(user=request.user).exists():
        user = request.user
        obj = User.objects.get(username=user)
        if Trainer.objects.filter(user=obj).exists():
            obj = Trainer.objects.get(user=obj)
            return render(request, 'trainer_profile.html', {'user': obj, "trainer": "trainer"})
        return render(request, 'trainer_profile.html', {'user': obj})
    else:
        return redirect('trainerLogin')

    
# @login_required
# def trainerProfile(request):
#     return render(request, 'trainer_profile.html')

@login_required
def ownerProfile(request):
        # return redirect('clientLogin')
        return render(request, 'owner_profile.html', {"owner": "owner"})
    
    #return render(request, 'owner_profile.html')
    
@login_required(login_url='clientLogin')
def logoutUser(request):
    if Client.objects.filter(user=request.user).exists():
        logout(request)
        return redirect('clientLogin')
    elif Trainer.objects.filter(user=request.user).exists():
        logout(request)
        return redirect('trainerLogin')
    elif Owner.objects.filter(user=request.user).exists():
        logout(request)
        return redirect('ownerLogin')
    else:
        logout(request)
        return redirect('clientLogin')






@login_required(login_url='clientLogin')
def discussionClientView(request):
    if Client.objects.filter(user=request.user).exists():
        user = request.user
        discussion = Discussion.objects.all()
        context = {
            'complain': discussion[::-1]
        }
        return render(request, 'discussion_client_view.html', context)
    else:
        return redirect('clientLogin')

@login_required(login_url='trainerLogin')
def discussionTrainerView(request):
    if Trainer.objects.filter(user=request.user).exists():
        cuser = Trainer.objects.get(user=request.user)
        discussion = Discussion.objects.all()
        context = {
            'discussion': discussion[::-1]
        }
        if request.method == 'POST' and request.POST['status'] == 'resolved':
            dnum = request.POST['dnum']
            status = "resolved"
            resolved_by = cuser
            discussion = Discussion.objects.get(dnumber=dnum)
            discussion.status = status
            discussion.resolved_by = resolved_by
            discussion.save()
            return redirect('discussiontrainerView')
        elif request.method == 'POST' and request.POST['status'] == 'rejected':
            dnum = request.POST['dnum']
            status = "rejected"
            resolved_by = cuser
            discussion = Discussion.objects.get(dnumber=dnum)
            discussion.status = status
            discussion.resolved_by = resolved_by
            discussion.save()
            return redirect('discussiontrainerView')
        return render(request, 'discussion_trainer_view.html', context)
    else:
        return redirect('trainerLogin')

@login_required(login_url='clientLogin')
def postDiscussion(request):
    if Client.objects.filter(user=request.user).exists():
        cuser = Client.objects.get(user=request.user)
        if request.method == 'POST':
            tag = request.POST['tag']
            statement = request.POST['statement']
            discussion = Discussion.objects.create(tag=tag, statement=statement, datetime = datetime.now(), posted_by=cuser)
            discussion.save()
            return redirect('discussionClientView')
        return render(request, 'post_discussion.html')
    else:
        return redirect('clientLogin')




@login_required(login_url='trainerLogin')
def TrainerPlanView(request):
    if Trainer.objects.filter(user=request.user).exists():
        plans = Plan.objects.all().order_by('plan_id')
        if request.method == 'POST':
            plan_id = request.POST['plan_id']
            plan = Plan.objects.get(plan_id=plan_id)
            plan.delete()
        return render(request, 'trainer_plan_view.html', {'plans': plans})
    else:
        return redirect('trainerLogin')

@login_required(login_url='trainerLogin')
def addPlan(request):
    if Trainer.objects.filter(user=request.user).exists():
        if request.method == 'POST':
            plan_id = request.POST['plan_id']
            plan_name = request.POST['pname']
            plan_description = request.POST['description']
            plan_point = request.POST['point']
            plan_trainer = request.POST['trainer']
            plan_topic = request.POST['topic']

            if plan_point.isdigit() == False:
                messages.info(request, 'Points must be a number')
                return redirect('addPlan')
            else:
                plan = Plan.objects.create(plan_id=plan_id, plan_name=plan_name, plan_description=plan_description, plan_point=plan_point, plan_trainer=plan_trainer, plan_topic=plan_topic)
                plan.save()
                return redirect('TrainerPlanView')
        return render(request, 'add_plan.html')
    else:
        return redirect('trainerLogin')




@login_required(login_url='trainerLogin')
def planView(request):
    if Trainer.objects.filter(user=request.user).exists():
        plan = Plan.objects.all().order_by('plan_id')
        return render(request, 'plan_view.html', {'plan': plan})
    else:
        return redirect('trainerLogin')




@login_required(login_url='trainerLogin')
def planContent(request, plan_id):
    if Trainer.objects.filter(user=request.user).exists():
        plan_content = Plan_Content.objects.all()[::-1]
        return render(request, 'plan_content.html', {'content':plan_content , 'plan_id': plan_id})
    else:
        return redirect('trainerLogin')


@login_required(login_url='trainerLogin')
def addPlanContent(request, plan_id):
    if Trainer.objects.filter(user=request.user).exists():
        plan_id = Plan.objects.get(plan_id=plan_id)
        user = request.user
        if Trainer.objects.filter(user=user).exists():
            user = Trainer.objects.get(user=user)
        if request.method == 'POST':
            plan_content_tag = request.POST['tag']
            plan_content_description = request.POST['description']
            img = request.FILES.get('image')

            plan_content = Plan_Content.objects.create(plan_id=plan_id, plan_content_tag=plan_content_tag, plan_content_description=plan_content_description, content_img=img, datetime = datetime.now(), upload_by=user)
            plan_content.save()
            return redirect(f'/plan-content/{plan_id}/')
        return render(request, 'add_plan_content.html', {'plan_id': plan_id})
    else:
        return redirect('trainerLogin')



@login_required(login_url='clientLogin')
def planviewClient(request):
    if Client.objects.filter(user=request.user).exists():
        planviewClient = Plan.objects.all().order_by('plan_id')
        return render(request, 'planviewClient.html', {'planviewClient': planviewClient})
    else:
        return redirect('clientLogin')


@login_required(login_url='clientLogin')
def planContentviewClient(request, plan_id):
    if Client.objects.filter(user=request.user).exists():
        planContentviewClient = Plan_Content.objects.all()[::-1]
        return render(request, 'planContentviewClient.html', {'planContentviewClient':planContentviewClient , 'plan_id': plan_id})
    else:
        return redirect('clientLogin')


#! WORKOUT PLAN

# @login_required(login_url='trainerLogin')
# def wplanView(request):
#     if Trainer.objects.filter(user=request.user).exists():
#         wplan = wPlan.objects.all().order_by('wplan_id')
#         return render(request, 'trainer_wplan_view.html', {'wplan': wplan})
#     else:
#         return redirect('trainerLogin')
@login_required(login_url='trainerLogin')
def wplanView(request):
    if Trainer.objects.filter(user=request.user).exists():
        wplan = wPlan.objects.all().order_by('wplan_id')
        if request.method == 'POST':
            print(request.POST)
            wplan_id = request.POST['wplan_id']
            wplans = wPlan.objects.get(wplan_id=wplan_id)
            wplans.delete()
        return render(request, 'trainer_wplan_view.html', {'wplan': wplan})
    else:
        return redirect('trainerLogin')



@login_required(login_url='clientLogin')
def wplanviewClient(request):
    if Client.objects.filter(user=request.user).exists():
        wplanviewClient = wPlan.objects.all().order_by('wplan_id')
        return render(request, 'wplanviewClient.html', {'wplanviewClient': wplanviewClient})
    else:
        return redirect('clientLogin')


@login_required(login_url='clientLogin')
def wplanContentviewClient(request, wplan_id):
    if Client.objects.filter(user=request.user).exists():
        wplanContentviewClient = wPlan_Content.objects.all()[::-1]
        return render(request, 'wplanContentviewClient.html', {'wplanContentviewClient':wplanContentviewClient , 'wplan_id': wplan_id})
    else:
        return redirect('clientLogin')
    












@login_required(login_url='trainerLogin')
def addwPlan(request):
    if Trainer.objects.filter(user=request.user).exists():
        if request.method == 'POST':
            wplan_id = request.POST['wplan_id']
            wplan_name = request.POST['wname']
            wplan_description = request.POST['wdescription']
            wplan_point = request.POST['wpoint']
            wplan_trainer = request.POST['wtrainer']
            wplan_topic = request.POST['wtopic']
            wplan_image = request.FILES.get('wplan_image')

            if wplan_point.isdigit() == False:
                messages.info(request, 'Points must be a number')
                return redirect('addwPlan')
            else:
                wplan = wPlan.objects.create(wplan_id=wplan_id, wplan_name=wplan_name, wplan_description=wplan_description, wplan_point=wplan_point, wplan_trainer=wplan_trainer, wplan_topic=wplan_topic, wplan_image=wplan_image)
                wplan.save()
                return redirect('wplanView')
        return render(request, 'add_work_plan.html')
    else:
        return redirect('trainerLogin')

@login_required(login_url='trainerLogin')
def addwPlanContent(request, wplan_id):
    if Trainer.objects.filter(user=request.user).exists():
        # Retrieve the wPlan instance by its ID
        wplan = wPlan.objects.get(wplan_id=wplan_id)
        user = request.user
        trainer = Trainer.objects.get(user=user)

        if request.method == 'POST':
            wplan_content_tag = request.POST.get('tag')
            wplan_content_description = request.POST.get('description')
            img = request.FILES.get('image')
            countdown_img = request.FILES.get('countdown')  # Assuming countdown is a file field in the form

            # Create and save a new wPlan_Content instance
            wplan_content = wPlan_Content.objects.create(
                wplan_id=wplan,  # Associate with the retrieved wPlan
                wplan_content_tag=wplan_content_tag,
                wplan_content_description=wplan_content_description,
                wcontent_img=img,
                wcontent_count=countdown_img,  # Assign the countdown image
                # wdatetime=timezone.now(), 
                wdatetime = datetime.now(),
                 
                  # Use timezone.now() for current time
                wupload_by=trainer  # Associate with the retrieved Trainer
            )
            wplan_content.save()

            return redirect(f'/wplan-content/{wplan_id}/')  # Redirect to a page that lists content or shows details for the wPlan

        return render(request, 'add_wplan_content.html', {'wplan_id': wplan_id})
    else:
        return redirect('trainerLogin')






@login_required(login_url='trainerLogin')
def wplanContent(request, wplan_id):
    if Trainer.objects.filter(user=request.user).exists():
        wplan_content = wPlan_Content.objects.all()[::-1]
        return render(request, 'trainer_wplan_content.html', {'wcontent':wplan_content , 'wplan_id': wplan_id})
    else:
        return redirect('trainerLogin')






@login_required
def delete_account(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        user = authenticate(username=request.user.username, password=password)
        if user is not None:
            user.delete()
            logout(request)
            messages.success(request, "Account deleted successfully")
            return redirect('clientLogin')
        else:
            messages.error(request, "Account deletion failed, password incorrect.")
            return redirect('clientProfile')
    else:
        return redirect('clientProfile')

@login_required
def editProfile(request):
    user = request.user
    client = Client.objects.get(user=user)

    if request.method == 'POST':
        client.client_usrname = request.POST.get('clientusrname', client.client_usrname)
        client.first_name = request.POST.get('first_name', client.first_name)
        client.last_name = request.POST.get('last_name', client.last_name)
        client.email = request.POST.get('email', client.email)
        client.phone = request.POST.get('phone', client.phone)
        client.age = request.POST.get('age', client.age)
        client.weight = request.POST.get('weight', client.weight)
        client.height = request.POST.get('height', client.height)
        client.bio = request.POST.get('bio', client.bio)
        client.gender = request.POST.get('gender', client.gender)
        client.achievement = request.POST.get('achievement', client.achievement)
        client.personalTrainer = request.POST.get('personalTrainer', client.personalTrainer)

        client.save()
        messages.success(request, 'Profile updated successfully')
        return redirect('clientProfile') 
        
    return render(request, 'edit_profile.html', {'client': client})

def index(request):
    return render(request,'emailapp/index.html')
    




def custom_message(request):
    #getting information from the form
    if request.method == "POST":
        form = CustomForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data['message']
            subject = form.cleaned_data['subject']
            print(message)
            
            #sending  email 
            clients = Client.objects.all()
            print(clients)    
            for clients in clients:
                print(clients.client_usrname)
                email = clients.email
                context = {'name': clients.client_usrname,'message': message}
                email_template = get_template('emailapp/email.html').render(context)
                email_address = EmailMessage(subject, email_template,"Fitlife Platform", [email])
                email_address.content_subtype = "html" 
                email_address.send()
            return redirect('custom_message')
        else:
            print(form.errors)
    return render(request,'emailapp/message.html')

def support_view(request):
    return render(request, 'support&faq.html')


def calculate_bmi(height_in_meters, weight_in_kg):

    return weight_in_kg / (height_in_meters ** 2)

def get_bmi_comment(bmi_value):
    if bmi_value < 18.5:
        return "Underweight"
    elif 18.5 <= bmi_value < 24.9:
        return "Good"
    elif 25 <= bmi_value < 30:
        return "Overweight"
    else:
        return "Obese"

@login_required
def bmi_page(request):
    user = request.user
    bmi_records = BMIRecord.objects.filter(user=user).order_by('recorded_at')


    if request.method == "POST":
        form = BMIForm(request.POST)
        if form.is_valid():
            height_in_inches = form.cleaned_data['height_in_inches']
            weight_in_kg = form.cleaned_data['weight_in_kg']
            height_in_meters = height_in_inches * 0.0254
            bmi_value = round(calculate_bmi(height_in_meters, weight_in_kg), 2)
            comment = get_bmi_comment(bmi_value)
            # Save the new BMI record
            bmi_record = BMIRecord.objects.create(
                user=user,
                height_in_meters=height_in_meters,
                weight_in_kg=weight_in_kg,
                bmi_value=bmi_value,
                comment=comment
            )
            return redirect('bmi_page')
    else:
        form = BMIForm()

    latest_bmi = bmi_records.last()

    context = {
        'form': form,
        'latest_bmi': latest_bmi,
        'bmi_records': bmi_records,
    }
    return render(request, 'bmi_page.html', context)

def workout_options(request):
    return render(request, 'workout_options.html')

def arms_beginner(request):
    # Replace with appropriate view logic and template
    return render(request, 'arms_beginner.html')

def arms_intermediate(request):
    # Replace with appropriate view logic and template
    return render(request, 'arms_intermediate.html')

def arms_advanced(request):
    # Replace with appropriate view logic and template
    return render(request, 'arms_advanced.html')

def chest_beginner(request):
    # Replace with appropriate view logic and template
    return render(request, 'chest_beginner.html')

def chest_intermediate(request):
    # Replace with appropriate view logic and template
    return render(request, 'chest_intermediate.html')

def chest_advanced(request):
    # Replace with appropriate view logic and template
    return render(request, 'chest_advanced.html')

def abs_beginner(request):
    # Replace with appropriate view logic and template
    return render(request, 'abs_beginner.html')

def abs_intermediate(request):
    # Replace with appropriate view logic and template
    return render(request, 'abs_intermediate.html')

def abs_advanced(request):
    # Replace with appropriate view logic and template
    return render(request, 'abs_advanced.html')

def legs_beginner(request):
    # Replace with appropriate view logic and template
    return render(request, 'legs_beginner.html')

def legs_intermediate(request):
    # Replace with appropriate view logic and template
    return render(request, 'legs_intermediate.html')

def legs_advanced(request):
    # Replace with appropriate view logic and template
    return render(request, 'legs_advanced.html')


def tracker(request):
    import json
    import requests
    if request.method == 'POST':
        query = request.POST['query']
        api_url = 'https://api.api-ninjas.com/v1/nutrition?query='
        api_request = requests.get(api_url + query, headers={'X-Api-Key': 'IF7UO25/zTEhl8LgzwncKw==EXlc6j1YbuGyqgJm'})
        try:
            api = json.loads(api_request.content)
            print(api_request.content)
        except Exception as e:
            api = "oops! There was an error"
            print(e)
        return render(request, 'tracker.html', {'api': api})
    else:
        return render(request, 'tracker.html', {'query': 'Enter a valid query'})

