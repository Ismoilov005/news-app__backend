from django import forms
from .models import CustomUser

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'bio', 'phone', 'avatar']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
        }
