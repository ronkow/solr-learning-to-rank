from django.contrib import admin

from .models import ModelTopic, ModelQuiz, ModelQuestion

class ModelTopicAdmin(admin.ModelAdmin):
    list_display = ('id', 'topic_name', 'topic_examples', 'topic_slug')
    prepopulated_fields = {"topic_slug": ("topic_name",)}

admin.site.register(ModelTopic, ModelTopicAdmin)

class ModelQuizAdmin(admin.ModelAdmin):
    list_display = ('id', 'quiz_topic', 'quiz_number')

admin.site.register(ModelQuiz, ModelQuizAdmin)

class ModelQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'q_quiz', 'q_topic', 'q_question', 'q_answer')

admin.site.register(ModelQuestion, ModelQuestionAdmin)
