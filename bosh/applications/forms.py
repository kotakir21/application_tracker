from django import forms
from .models import Application, ApplicationStatus, Comment
from programs.models import Program

class ProgramApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = [
            'full_name', 'email', 'phone',
            'resume', 'passport', 'cover_letter', 'travel_plan'
        ]
        widgets = {
            'travel_plan': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        program = kwargs.pop('program', None)
        super(ProgramApplicationForm, self).__init__(*args, **kwargs)

        if user:
            self.fields['full_name'].initial = f"{user.first_name} {user.last_name}"
            self.fields['email'].initial = user.email
            self.fields['phone'].initial = user.profile.phone  # Assuming phone is stored in the user's profile

        if program:
            # Manually set the program field as a hidden input
            self.fields['program'] = forms.ModelChoiceField(
                queryset=Program.objects.filter(id=program.id),
                initial=program,
                widget=forms.HiddenInput()
            )

class ApplicationStatusForm(forms.ModelForm):
    class Meta:
        model = ApplicationStatus
        fields = [
            'status', 'comments', 'additional_documents_required', 
            'additional_documents_description', 'additional_documents'
        ]

    def __init__(self, *args, **kwargs):
        super(ApplicationStatusForm, self).__init__(*args, **kwargs)
        # Make additional documents fields optional unless specifically required
        if not self.instance.additional_documents_required:
            self.fields['additional_documents'].required = False
            self.fields['additional_documents_description'].required = False

class AdditionalDocumentsForm(forms.ModelForm):
    class Meta:
        model = ApplicationStatus
        fields = ['additional_documents']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text', 'attachment']

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['text'].widget.attrs.update({
            'placeholder': 'Write a comment...',
            'rows': 3,
        })
        self.fields['attachment'].label = 'Attach a file (optional)'
