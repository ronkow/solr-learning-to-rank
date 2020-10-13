from django.db import models
from django.urls import reverse


class ModelQuestionbank(models.Model):
    qb_topic = models.ForeignKey('appquiz.ModelTopic', on_delete=models.CASCADE, related_name='modelqbtopic')
    qb_question = models.TextField(unique=True)
    qb_answer = models.CharField(max_length=50)
    qb_choice1 = models.CharField(max_length=50)
    qb_choice2 = models.CharField(max_length=50)
    qb_choice3 = models.CharField(max_length=50)

    def __str__(self):
        return self.qb_question
