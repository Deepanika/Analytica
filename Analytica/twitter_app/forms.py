    
from django import forms
from . import models
     
           
class RegistrationForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = ["username","email",'password']
        widgets={
            'password':forms.PasswordInput()
        }