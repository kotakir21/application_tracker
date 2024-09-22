from django.db import models
from custom_user.models import User
from programs.models import Program

class Application(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    resume = models.FileField(upload_to='resumes/')
    passport = models.FileField(upload_to='passports/')
    cover_letter = models.FileField(upload_to='cover_letters/', default='path/to/default_cover_letter.pdf')
    travel_plan = models.DateField()
    date_of_application = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='Submitted')
    current_status = models.ForeignKey('ApplicationStatus', on_delete=models.SET_NULL, null=True, blank=True, related_name='applications')

    def __str__(self):
        return f"{self.full_name} - {self.program.name}"

    def get_timeline_events(self):
        events = [{
            'timestamp': self.date_of_application,
            'description': f"Application submitted by {self.full_name}."
        }]
        statuses = self.statuses.all().order_by('date_updated')
        for status in statuses:
            events.append({
                'timestamp': status.date_updated,
                'description': f"Status updated to '{status.status}' by {status.officer.get_full_name()}."
            })
            if status.comments:
                events.append({
                    'timestamp': status.date_updated,
                    'description': f"Comment added: '{status.comments}' by {status.officer.get_full_name()}."
                })
        comments = self.comments.all().order_by('created_at')
        for comment in comments:
            events.append({
                'timestamp': comment.created_at,
                'description': f"Comment added by {comment.user.get_full_name()}: '{comment.text}'."
            })
        return sorted(events, key=lambda x: x['timestamp'])

class ApplicationStatus(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='statuses')
    status = models.CharField(max_length=255)
    officer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    comments = models.TextField(blank=True, null=True)
    date_updated = models.DateTimeField(auto_now_add=True)
    additional_documents_required = models.BooleanField(default=False)
    additional_documents_description = models.TextField(blank=True, null=True)  # Describes what documents are needed
    additional_documents = models.FileField(upload_to='additional_documents/', blank=True, null=True)

    def __str__(self):
        return f"{self.application.full_name} - {self.status} ({self.date_updated})"

class Comment(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    attachment = models.FileField(upload_to='comment_attachments/', blank=True, null=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.application.program.name}"
