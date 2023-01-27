from django.urls import path

from . import views

app_name = 'appsearch'

urlpatterns = [
    # LTR SEARCH
    path('ltr/', views.ltrsearch_view, name = 'ltrsearchview'),

    path('ltr_q/',
        views.ltrsearch_result_view,
        name = 'ltrsearchresultview'),

    
    # RECOMMEND TOP 10 QUESTIONS IN QUIZ RESULTS PAGE
    path('recommend/<arg_question>/<arg_answer>/',
        views.recommend_view,
        name = 'recommendview'),


    path('',
        views.TopicView,
        name = 'searchview'),

    # SEARCH RESULTS (TOPIC)
    path('topic/',
        views.searchtopic_view,
        name = 'searchtopicview'),

    # SEARCH RESULTS (QUESTION TEXT, ANSWER CHOICE TEXT)
    path('kw/',
        views.searchtext_view,
        name = 'searchtextview'),


    path('qbsession/<int:arg_question_id>/',
        views.qbsession_view,
        name='qbsessionview'),

    path('qbdisplay/<int:arg_question_id>/',     # question display
         views.qbdisplay_view,
         name='qbdisplayview'),

    path('qbresult/<int:arg_question_id>/',      # question answer
         views.qbresult_view,
         name='qbresultview'),
]