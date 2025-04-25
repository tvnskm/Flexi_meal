from django import forms
import re
from django.core.exceptions import ValidationError

def validate_phone(value):
    if not re.fullmatch(r'\d{10}', value):
        raise ValidationError('Enter a valid 10-digit phone number')

class OrderForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        error_messages={'required': 'Name is required'}
    )
    email = forms.EmailField(
        error_messages={
            'required': 'Email is required',
            'invalid': 'Enter a valid email address'
        }
    )
    phone = forms.CharField(
        validators=[validate_phone],
        error_messages={
            'required': 'Phone number is required',
            'invalid': 'Enter a valid 10-digit phone number'
        }
    )
    address = forms.CharField(
        widget=forms.Textarea,
        error_messages={'required': 'Address is required'}
    )
