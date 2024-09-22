# dashboard/forms.py

from django import forms
from applications.models import ApplicationStatus

class StatusForm(forms.ModelForm):
    class Meta:
        model = ApplicationStatus
        fields = ['status', 'additional_documents_required']

class CommentForm(forms.Form):
    comments = forms.CharField(widget=forms.Textarea, required=False, label="Add Comment")
