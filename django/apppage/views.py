from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.core.mail import BadHeaderError, EmailMessage
from django.http import HttpResponse, HttpResponseRedirect

from .forms import ContactForm

class HomeView(TemplateView):
    template_name = 'page/home.html'

class AboutView(TemplateView):
    template_name = 'page/about.html'


class ModelView(TemplateView):
    template_name = 'data/model.html'

class ResultView(TemplateView):
    template_name = 'data/result.html'

class ProfileView(TemplateView):
    template_name = 'page/profile.html'


def SuccessView(request):
    return render(request, "page/contact_success.html")

class SettingsView(TemplateView):
    template_name = 'page/password_change.html'

def ContactView(request):
    if request.method == 'GET':
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_email   = form.cleaned_data['my_email_address']
            contact_subject = form.cleaned_data['subject']
            contact_message = form.cleaned_data['message']

            try:
                EmailMessage(
                    subject    = contact_subject,
                    body       = contact_message,
                    from_email = 'do-not-reply@ronkow.com',
                    to         = ['admin@ronkow.com'],
                    reply_to   = [contact_email],
                ).send()
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect('apppage:successview')
    return render(request, "page/contact_form.html", {'form': form})
