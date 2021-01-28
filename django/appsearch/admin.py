from django.contrib import admin

from .models import ModelQuestionbank

class ModelQuestionbankAdmin(admin.ModelAdmin):

    list_display = ('id', 'qb_topic', 'qb_question', 'qb_answer', 'qb_choice1', 'qb_choice2', 'qb_choice3')

admin.site.register(ModelQuestionbank, ModelQuestionbankAdmin)
