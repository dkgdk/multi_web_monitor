from django import forms
from .models import Website


class WebsiteForm(forms.ModelForm):
    class Meta:
        model = Website
        fields = ['name', 'url', 'check_interval', 'timeout', 'notify_email', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. My Company Site',
            }),
            'url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com',
            }),
            'check_interval': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 60,
            }),
            'timeout': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 5,
                'max': 120,
            }),
            'notify_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'alerts@example.com',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
        labels = {
            'check_interval': 'Check Interval (minutes)',
            'timeout': 'Timeout (seconds)',
            'notify_email': 'Alert Email (optional)',
            'is_active': 'Active Monitoring',
        }
