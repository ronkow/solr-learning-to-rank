from django.db import models

from django.urls import reverse


class ModelTopic(models.Model):

    topic_name  = models.CharField(max_length=100, unique=True)
    topic_examples = models.TextField(null=True)

    topic_slug   = models.SlugField()

    # to display topic_name instead of id for question_topic in ModelQuestion
    def __str__(self):
        return self.topic_name


class ModelQuiz(models.Model):
    QUIZ_NUMBER = (
        (1, 'Quiz 1'),
        (2, 'Quiz 2'),
        (3, 'Quiz 3'),
    )

    quiz_topic = models.ForeignKey(ModelTopic, on_delete=models.CASCADE, related_name='modelquiztopic')
    quiz_number = models.IntegerField(choices=QUIZ_NUMBER)

    def __str__(self):
        return f'{self.quiz_number}:{self.quiz_topic}'


class ModelQuestion(models.Model):

    q_topic = models.ForeignKey(ModelTopic, on_delete=models.CASCADE, related_name='modelquestiontopic')
    q_quiz = models.ForeignKey(ModelQuiz, on_delete=models.CASCADE, related_name='modelquestionquiz')
    
    q_question = models.TextField(unique=True)
    q_answer = models.CharField(max_length=50)
    q_choice1 = models.CharField(max_length=50)
    q_choice2 = models.CharField(max_length=50)
    q_choice3 = models.CharField(max_length=50)

    # to display question_text instead of id for choice_question in ModelChoice
    def __str__(self):
        return self.q_question