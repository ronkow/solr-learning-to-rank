from django import forms

class ContactForm(forms.Form):
    your_email_address = forms.EmailField(required=True, widget=forms.TextInput(attrs={'placeholder': 'E-mail address', 'autofocus':'true'}) )
    subject            = forms.CharField(required=True)
    message            = forms.CharField(widget=forms.Textarea, required=True)
