from django.http import HttpResponseRedirect
from django.urls import reverse

from django.shortcuts import render, redirect
from django.views.generic import ListView
from random import shuffle

from .models import ModelTopic, ModelQuestion, ModelQuiz


def topic_view(request):
    topic = ModelTopic.objects.all()
    context = {'context_topic': topic}

    return render(request, 'quiz/topic.html', context)


def quizlist_view(request, arg_topic_id):

    topic =  ModelTopic.objects.get(id = arg_topic_id)
    quiz = ModelQuiz.objects.filter(quiz_topic = arg_topic_id)

    context = {'context_topic': topic, 'context_quiz': quiz}

    return render(request, 'quiz/quiz_list.html', context)


# helper function for quizsession_view()
# RETURNS A LIST [answer, choice1, choice2, choice3]

def question_choices(q):

    all_choices = [q.q_answer]
    
    if q.q_choice1 != 'na':
        all_choices.append(q.q_choice1)

    if q.q_choice2 != 'na':
        all_choices.append(q.q_choice2)

    if q.q_choice3 != 'na':
        all_choices.append(q.q_choice3)
        
    shuffle(all_choices)
    
    return all_choices
    

# helper function for quizdisplay_view()

def check_answer(question_answer, user_answer):

    if user_answer == question_answer:
        return True
    else:
        return False


# ON SELECTING A QUIZ, 
# START quizsession_view

def quizsession_view(request, arg_topic_id, arg_quiz_number):

    quiz = ModelQuiz.objects.get(quiz_topic = arg_topic_id, quiz_number = arg_quiz_number)
    quiz_id = quiz.id

    # ALL QUESTIONS FOR THE SELECTED QUIZ
    questions = ModelQuestion.objects.filter(q_quiz = quiz_id)

    # CLEAR OLD SESSION
    try:
        del request.session['quiz']
        del request.session['progress']
        del request.session['shuffled']
        del request.session['user']
    except KeyError:
        pass

    # NEW SESSION NAMED quiz
    # STORES A DICT quiz_id : { qid1 : { answer : False, choice1 : False, ...} }
    # q.id IS QUESTION ID
    request.session['quiz'] = {
        quiz_id: {
            q.id : { c : False for c in question_choices(q) } for q in questions
        }
    }

    # NEW SESSION NAMED progress
    # STORES A DICT quiz_id : { 'remaining_question_ids' : [qid1, qid2, qid3, qid4, qid5] }
    request.session['progress'] = {
        quiz_id : {
            'remaining_question_ids' : [q.id for q in questions]       # list of question ids
        }
    }

    # SET SESSION NEVER EXPIRE
    request.session.set_expiry(0)

    # SHUFFLE REMAINING QUESTION IDS
    shuffle( request.session['progress'][quiz_id]['remaining_question_ids'] )
    
    # NEW SESSION NAMED shuffled
    request.session['shuffled'] = request.session['progress']

    # CURRENT QUESTION ID = FIRST ITEM IN progress 
    current_question_id = request.session['progress'][quiz_id]['remaining_question_ids'][0]
    
    # GET CURRENT QUESTION
    current_question = ModelQuestion.objects.get(id = current_question_id)

    # FIRST QUESTION NUMBER
    current_question_number = 1

    # NEW SESSION NAMED user
    request.session['user'] = {}

    return redirect('appquiz:quizdisplayview', arg_topic_id, arg_quiz_number, quiz_id, current_question_id, current_question_number)



# PASS INTO THIS FUNCTION ONE topic id, quiz number, quiz id, question id, question number
def quizdisplay_view(request, arg_topic_id, arg_quiz_number, arg_quiz_id, arg_current_question_id, arg_current_question_number):

    if not request.session['quiz']:
        return redirect('appquiz:quizsessionview', arg_topic_id, arg_quiz_number)

    # LIST OF REMAINING QUESTION IDS
    list_question_ids = request.session['shuffled'][str(arg_quiz_id)]['remaining_question_ids']

    # GET TOPIC, QUIZ, QUESTION
    topic = ModelTopic.objects.get(id = arg_topic_id)
    quiz = ModelQuiz.objects.get(id = arg_quiz_id)
    current_question  = ModelQuestion.objects.get(id=arg_current_question_id)

    dict_choices = request.session['quiz'][str(arg_quiz_id)][str(arg_current_question_id)]
    list_choices = [ c for c in dict_choices ]

    # FOR QUESTION NUMBER COUNT Question x of y
    progress_current = arg_current_question_number
    progress_total = len( request.session['quiz'][str(arg_quiz_id)] )

    first_question = False
    if progress_current == 1:
        first_question = True

    one_question = False
    if progress_total == 1:
        one_question = True

    context = {
        'context_topic'           : topic,
        'context_quiz'            : quiz,
        
        'context_first_question'  : first_question,
        'context_one_question'    : one_question,

        'context_progress_current': progress_current,
        'context_progress_total'  : progress_total,

        'context_current_question' : current_question,
        'context_list_choices'     : list_choices,
    }

    # SESSION QUIZ
    if request.method == 'POST':

        # TO BE SIMPLIFIED TO ORIGINAL CODE
        # IF try IS SUCCESSFUL, else CODE IS RUN
        try:
            user_answer_selected = request.POST.get(str(quiz.id))

        except KeyError:
            return render(request, 'quiz/quiz_display.html', context)

        else:
            # IF USER SELECTED ANSWER = 
            request.session['quiz'][str(arg_quiz_id)][str(arg_current_question_id)].update(
                {c: True for c in list_choices if current_question.q_answer == c}
            )

            current_question_choices = { c: true_or_false for c, true_or_false in request.session['quiz'][str(arg_quiz_id)][str(arg_current_question_id)].items() }

            # ADD DATA TO user
            request.session['user'].update( {
                    str(arg_current_question_id) : {
                        'user' : {
                            'question_text'         : current_question.q_question,                  
                            'question_choices'      : current_question_choices,
                            'user_answer_selected'  : request.POST.get(str(quiz.id)),     # 'user_answer_selected' : user_answer_selected
                            'user_answer_check'     : check_answer(current_question.q_answer, request.POST.get(str(quiz.id))), # check_answer(current_question.q_answer, user_answer_selected)
                        }
                    }
            })

            request.session.modified = True

            try:
                current_question_number = arg_current_question_number + 1
                current_question_id = list_question_ids[current_question_number-1]

                # BACK TO START OF THIS FUNCTION
                return redirect('appquiz:quizdisplayview', arg_topic_id, arg_quiz_number, arg_quiz_id, current_question_id, current_question_number)

            # DISPLAY RESULT
            except IndexError:
                return redirect('appquiz:quizresultview', arg_topic_id, arg_quiz_number, arg_quiz_id)

    # IF NO POST, DISPLAY QUIZ. THIS IS TO DISPLAY THE FIRST QUESTION
    return render(request, 'quiz/quiz_display.html', context)



def quizresult_view(request, arg_topic_id, arg_quiz_number, arg_quiz_id):

    if not request.session['quiz']:
        return redirect('appquiz:quizsessionview', arg_topic_id, arg_quiz_number)

    topic = ModelTopic.objects.get(id = arg_topic_id)

    list_question_ids = request.session['shuffled'][str(arg_quiz_id)]['remaining_question_ids']

    # NEW DICT
    dict_quiz = {qid : request.session['user'][str(qid)] for qid in list_question_ids}.items()

    q_all     = 0
    q_correct = 0

    for key, val in dict_quiz:
        q_all += 1
        if val['user']['user_answer_check']:
            q_correct += 1

    result = int((q_correct/q_all)*100)

    context = {
        'context_topic': topic,
        'context_quiz_number': arg_quiz_number,

        'context_result'  : result,
        'context_dict_quiz' : dict_quiz,
    }

    return render(request, 'quiz/result.html', context)