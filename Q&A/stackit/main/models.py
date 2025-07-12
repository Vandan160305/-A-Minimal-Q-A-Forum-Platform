from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class Question(models.Model):
    author = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, null=False)
    body = models.TextField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_responses(self):
        return self.responses.filter(parent=None)

class Response(models.Model):
    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, null=False, on_delete=models.CASCADE, related_name='responses')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    body = models.TextField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.body

    def get_responses(self):
        return Response.objects.filter(parent=self)


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('question', 'New Question'),
        ('response', 'New Response'),
        ('reply', 'New Reply'),
    )
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True, blank=True)
    response = models.ForeignKey(Response, on_delete=models.CASCADE, null=True, blank=True)
    text = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.sender.username} {self.notification_type} to {self.recipient.username}"
    
    class Meta:
        ordering = ['-created_at']


# Signal handlers for notifications
@receiver(post_save, sender=Question)
def create_question_notification(sender, instance, created, **kwargs):
    if created:
        # Notify all users except the author about the new question
        from django.contrib.auth.models import User
        users = User.objects.exclude(id=instance.author.id)
        
        for user in users:
            Notification.objects.create(
                recipient=user,
                sender=instance.author,
                notification_type='question',
                question=instance,
                text=f"New question: {instance.title}"
            )

@receiver(post_save, sender=Response)
def create_response_notification(sender, instance, created, **kwargs):
    if created:
        # If it's a direct response to a question, notify the question author
        if instance.parent is None:
            # Don't notify if the author is responding to their own question
            if instance.question.author != instance.user:
                Notification.objects.create(
                    recipient=instance.question.author,
                    sender=instance.user,
                    notification_type='response',
                    question=instance.question,
                    response=instance,
                    text=f"New response to your question: {instance.question.title}"
                )
        # If it's a reply to a response, notify the response author
        else:
            # Don't notify if the author is replying to their own response
            if instance.parent.user != instance.user:
                Notification.objects.create(
                    recipient=instance.parent.user,
                    sender=instance.user,
                    notification_type='reply',
                    question=instance.question,
                    response=instance,
                    text=f"New reply to your response on: {instance.question.title}"
                )
