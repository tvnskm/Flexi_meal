from django import forms

class OrderForm(forms.Form):
    name = forms.CharField(max_length=100, error_messages={'required': 'Name is required'})
    email = forms.EmailField(error_messages={'required': 'Email is required', 'invalid': 'Enter a valid email address'})
    phone = forms.CharField(max_length=15, min_length=10, error_messages={'required': 'Phone number is required', 'invalid': 'Enter a valid phone number'})
    address = forms.CharField(widget=forms.Textarea, error_messages={'required': 'Address is required'})