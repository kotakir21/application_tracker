from django import forms
from .models import User
from wagtail.users.forms import UserCreationForm, UserEditForm
from django.utils.translation import gettext_lazy as _

class WagtailUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User

class WagtailUserEditForm(UserEditForm):
    class Meta(UserEditForm.Meta):
        model = User

class SignupForm(forms.Form):
    first_name = forms.CharField(max_length=30, label=_("First name"))
    last_name = forms.CharField(max_length=30, label=_("Last name"))

    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        # Set the user type to 'is_customer'
        user.is_customer = True

        user.save()
        
