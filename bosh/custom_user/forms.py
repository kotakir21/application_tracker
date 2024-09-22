from django import forms
from django.utils.translation import gettext_lazy as _
from allauth.account.forms import SignupForm as AllauthSignupForm
from .models import Profile, User

# Custom Signup Form
class CustomSignupForm(AllauthSignupForm):
    first_name = forms.CharField(max_length=30, label=_("First Name"))
    last_name = forms.CharField(max_length=30, label=_("Last Name"))
    phone = forms.CharField(max_length=15, label=_("Phone Number"), required=False)

    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()

        # Save additional information to the user's profile if needed
        profile = Profile.objects.create(user=user)
        profile.phone = self.cleaned_data.get('phone', '')
        profile.save()

        return user

# User Profile Form
class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, label='First Name')
    last_name = forms.CharField(max_length=30, label='Last Name')

    class Meta:
        model = Profile
        fields = ['phone', 'profile_picture']
        widgets = {
            'profile_picture': forms.FileInput(),
        }

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name

    def save(self, commit=True):
        user = self.instance.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()

        profile = super(UserProfileForm, self).save(commit=False)
        if commit:
            profile.save()
        return profile
