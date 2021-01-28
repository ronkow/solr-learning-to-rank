from django.urls import path

from . import views

app_name = 'appquiz'

urlpatterns = [
    path('topic/',               
        views.topic_view, 
        name = 'topicview'),
    
    path('quizlist/<int:arg_topic_id>/',    
        views.quizlist_view,        
        name = 'quizlistview'),
    
    path('quizsession/<int:arg_topic_id>/<int:arg_quiz_number>/',
        views.quizsession_view,
        name='quizsessionview'),

    path('quizdisplay/<int:arg_topic_id>/<int:arg_quiz_number>/<int:arg_quiz_id>/<int:arg_current_question_id>/<int:arg_current_question_number>/',
         views.quizdisplay_view,
         name='quizdisplayview'),

    path('result/<int:arg_topic_id>/<int:arg_quiz_number>/<int:arg_quiz_id>/',
         views.quizresult_view,
         name='quizresultview'),
]