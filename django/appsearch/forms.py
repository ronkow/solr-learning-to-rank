from django import forms

from django.forms import ModelForm
from .models import ModelQuestionbank

class TopicForm(ModelForm):

    class Meta:
        model = ModelQuestionbank
        fields = ['qb_topic']           # fields = ('qb_topic')  works too?
        labels = { 'qb_topic': '' }

    def __init__(self, *args, **kwargs):
        super(TopicForm, self).__init__(*args, **kwargs)
        self.fields['qb_topic'].empty_label = 'Select a topic'