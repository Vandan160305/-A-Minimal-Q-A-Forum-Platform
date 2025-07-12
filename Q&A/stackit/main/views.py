from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from .models import Question, Response, Notification
from .forms import RegisterUserForm, LoginForm, NewQuestionForm, NewResponseForm, NewReplyForm
import uuid

# Create your views here.

def registerPage(request):
    form = RegisterUserForm()

    if request.method == 'POST':
        try:
            form = RegisterUserForm(request.POST)
            if form.is_valid():
                user = form.save()
                login(request, user)
                return redirect('index')
        except Exception as e:
            print(e)
            raise

    context = {
        'form': form
    }
    return render(request, 'register.html', context)


@login_required(login_url='register')
def notificationsPage(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    
    # Mark all as read
    unread = notifications.filter(is_read=False)
    unread.update(is_read=True)
    
    context = {
        'notifications': notifications
    }
    return render(request, 'notifications.html', context)


@login_required(login_url='register')
def markNotificationRead(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    
    # Check if it's an AJAX request
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    # For non-AJAX requests, redirect to the appropriate page
    if notification.question:
        return redirect('question', id=notification.question.id)
    else:
        return redirect('notifications')

def loginPage(request):
    form = LoginForm()

    if request.method == 'POST':
        try:
            form = LoginForm(data=request.POST)
            if form.is_valid():
                user = form.get_user()
                login(request, user)
                return redirect('index')
        except Exception as e:
            print(e)
            raise

    context = {'form': form}
    return render(request, 'login.html', context)

@login_required(login_url='register')
def logoutPage(request):
    logout(request)
    return redirect('login')

@login_required(login_url='register')
def newQuestionPage(request):
    form = NewQuestionForm()

    if request.method == 'POST':
        try:
            form = NewQuestionForm(request.POST)
            if form.is_valid():
                question = form.save(commit=False)
                question.author = request.user
                question.save()
                return redirect('index')
        except Exception as e:
            print(e)
            raise

    context = {'form': form}
    return render(request, 'new-question.html', context)

def homePage(request):
    questions = Question.objects.all().order_by('-created_at')
    
    # Get notifications if user is authenticated
    notifications = []
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(recipient=request.user, is_read=False)
    
    context = {
        'questions': questions,
        'notifications': notifications
    }
    return render(request, 'homepage.html', context)

def questionPage(request, id):
    response_form = NewResponseForm()
    reply_form = NewReplyForm()

    if request.method == 'POST':
        try:
            response_form = NewResponseForm(request.POST)
            if response_form.is_valid():
                response = response_form.save(commit=False)
                response.user = request.user
                response.question = Question.objects.get(id=id)
                response.save()
                return redirect('/question/'+str(id)+'#'+str(response.id))
        except Exception as e:
            print(e)
            raise

    question = Question.objects.get(id=id)
    
    # Get notifications if user is authenticated
    notifications = []
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(recipient=request.user, is_read=False)
    
    context = {
        'question': question,
        'response_form': response_form,
        'reply_form': reply_form,
        'notifications': notifications
    }
    return render(request, 'question.html', context)


@login_required(login_url='register')
def replyPage(request):
    if request.method == 'POST':
        try:
            form = NewReplyForm(request.POST)
            if form.is_valid():
                question_id = request.POST.get('question')
                parent_id = request.POST.get('parent')
                reply = form.save(commit=False)
                reply.user = request.user
                reply.question = Question.objects.get(id=question_id)
                reply.parent = Response.objects.get(id=parent_id)
                reply.save()
                return redirect('/question/'+str(question_id)+'#'+str(reply.id))
        except Exception as e:
            print(e)
            raise

    return redirect('index')


@login_required
def upload_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        # Generate a unique filename
        filename = f'uploads/{uuid.uuid4()}/{image.name}'
        # Save the file
        fs = FileSystemStorage()
        filename = fs.save(filename, image)
        file_url = fs.url(filename)
        return JsonResponse({'location': file_url})
    return JsonResponse({'error': 'No image provided'}, status=400)