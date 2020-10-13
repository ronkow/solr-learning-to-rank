from django.urls import path
from . import views

app_name = 'appsearch'

urlpatterns = [

    path('data/',
        views.DataView,
        name = 'dataview'),

    path('data/<int:arg_topic_id>/',
        views.DataListView,
        name = 'datalistview'),

    # LTR SEARCH
    path('ltr/',
        views.ltrsearch_view,
        name = 'ltrsearchview'),

    path('ltr_q/',
        views.ltrsearch_result_view,
        name = 'ltrsearchresultview'),

    # NO-LTR SEARCH
    path('',
        views.TopicView,
        name = 'searchview'),

    path('topic/',
        views.searchtopic_view,
        name = 'searchtopicview'),

    path('kw/',
        views.searchtext_view,
        name = 'searchtextview'),

    path('qbdisplay/<int:arg_question_id>/',     # question display
    	views.qbdisplay_view,
    	name='qbdisplayview'),

    path('qbresult/<int:arg_question_id>/',     # question answer
    	views.qbresult_view,
    	name='qbresultview'),

    path('qbsession/<int:arg_question_id>/',
        views.qbsession_view,
        name='qbsessionview'),
]
