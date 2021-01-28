from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render, redirect
from django.views.generic import ListView, TemplateView
from django.db.models import Q

from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger

import re
from random import shuffle

from .models import ModelQuestionbank
from .forms import TopicForm

# ------------------------------------------------------------------------------

import random    # random.randint
import os        # os.path.join
import csv       # csv.DictReader
import json      # json.dumps
import requests  # requests.post
import urllib    # urllib.parse.urlencode, urllib.parse.quote_plus
import re        # re.match
import socket

random.seed(1)

# ------------------------------------------------------------------------------

import nltk       # for POS tagging

nltk_downloader = nltk.downloader.Downloader()

if not nltk_downloader.is_installed('punkt'):
    nltk_downloader.download('punkt')
if not nltk_downloader.is_installed('averaged_perceptron_tagger'):
    nltk_downloader.download('averaged_perceptron_tagger')

#from pycorenlp import StanfordCoreNLP
#parser = StanfordCoreNLP('http://198.100.45.97:9000/')
# ------------------------------------------------------------------------------

from nltk.tree import *
from stanza.server import CoreNLPClient

client = CoreNLPClient(
    memory='4G',
    endpoint='http://localhost:9000',
    be_quiet=True,
    start_server='DONT_START'
)
client.start()

# ------------------------------------------------------------------------------

SOLR_URL = "http://localhost:8983/solr/core1"

# ------------------------------------------------------------------------------
# EXTRACT FEATURES FROM QUERY

# import time    
# time.sleep(10) 

def parse_tree(s):
    output = client.annotate( s, properties={'annotators': 'parse', 'outputFormat': 'json', 'timeout': 100000,} )
    if s:
        t = output['sentences'][0]['parse']
    else:
        t = ''
    if t:
        return Tree.fromstring(t)
    else:
        return ''

    
def parse_tree_productions(s):
    t1 = parse_tree(s)
    if t1:
        t2 = t1.productions()
    else:
        return ''
    t3 = []
    productions = ''
    for x in t2:
        if "'" in str(x) or "ROOT" in str(x): 
            continue
        else:
            t3.append(x)
    for p in t3:
        p1 = str(p).replace(" ->", "")
        p2 = p1.replace(" ", "_")
        if productions == '':
            productions = p2
        else:
            productions = productions + ' ' + p2
    return productions


def convert_list_tuple_to_string(x):
    s = ''
    for w in x:
        if s == '':
            s = w
        else:
            s = s + ' ' + w
    return s


def concat_string_with_underscore(s):
    t = s.split()
    s1 = ''
    for w in t:
        if s1 == '':
            s1 = w
        else:
            s1 = s1 + '_' + w
    return s1


def words_to_pos_tags(s):
    t = s.split()               
    word_tag = nltk.pos_tag(t)  
    tags = ''
    for p in word_tag:
        tag = p[1]              
        if tags == '':
            tags = tag
        else:
            tags = tags + ' ' + tag
    return tags


def ngram_list_to_string(ngram_list):
    s1 = ''
    for tup in ngram_list:
        s2 = convert_list_tuple_to_string(tup)
        s3 = concat_string_with_underscore(s2)
        if s1 == '':
            s1 = s3
        else:
            s1 = s1 + ' ' + s3
    return s1


def string_to_bigrams(s):
    t = s.split()
    bigram_list = list(nltk.ngrams(t,2))  
    return ngram_list_to_string(bigram_list)


def string_to_trigrams(s):
    t = s.split()
    trigram_list = list(nltk.ngrams(t,3))  
    return ngram_list_to_string(trigram_list)


def question_complete(q,a):
    return q.replace("*", a)


def n_words_before_answer(q,n):
    string_before = q.split('*')[0]                
    word_list = string_before.strip().split(' ')[-n:]
    return convert_list_tuple_to_string(word_list)


def n_words_after_answer(q,n):
    if q.endswith('*') or q == '':
        return ''
    else:
        string_after = q.split('*')[1]             

    word_list = string_after.strip().split(' ')[0:n]
    w = convert_list_tuple_to_string(word_list)
    if len(w) != 0:
        last_char = w[len(w)-1]
    if last_char == '.' or last_char == '?' or last_char == '!' or last_char == ',' or last_char == ';':
        words = w[:-1]
    else:
        words = w
    return words


def question_substring(q,a,n):
    s1 = n_words_before_answer(q,n)
    s2 = n_words_after_answer(q,n)
    return (s1 + ' ' + a + ' ' + s2).strip()    


def last_word_of_string(s):
    if s:
        s1 = s.split()
        return s1[-1]
    else:
        return ''

    
def first_word_of_string(s):
    if s:
        s1 = s.split()
        return s1[0]
    else:
        return ''

    
def answer_is_at_beginning_doc(q):
    t = q.split(' ',1)[0]        
    if t == '*':
        return 'b'
    else:
        return 'x'

    
def answer_is_at_end_doc(q):
    t = q.split('*')[1]          
    if t == '.' or t == '?' or t == '!':
        return 'e'
    else:
        return 'x'

    
def answer_is_at_beginning_query(q):
    t = q.split(' ',1)[0]        
    if t == '*':
        return 'b'
    else:
        return 'y'

    
def answer_is_at_end_query(q):
    t = q.split('*')[1]          
    if t == '.' or t == '?' or t == '!':
        return 'e'
    else:
        return 'y'

    
def string_length(s):
    return len(s.split())

#-------------------------------------------------------------------------------
# SOLR FUNCTIONS

def check_solr_status():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    solr = sock.connect_ex(('localhost', 8983))
    if solr != 0:
        return True
    else:
        return False


def send_query_to_solr(payload):
    params = urllib.parse.urlencode(payload, quote_via=urllib.parse.quote_plus)
    search_url = SOLR_URL + "/query?" + params
    resp = requests.get(search_url)
    resp_json = json.loads(resp.text)
    docs = resp_json["response"]["docs"]

    return docs


def get_documents_from_database(docs):
    result_list = []
    for doc in docs:
        doc_id = int(doc["id"])
        q = ModelQuestionbank.objects.get(id = doc_id)
        result_list.append(q)

    return result_list


# NO LTR SEARCH RESULTS
def no_ltr_search_result(query):
    payload = {
        "q": query,
        "defType": "edismax",
        "qf": "qa",         
        "fl": "id",
        "rows": 1002,
    }
    docs = send_query_to_solr(payload)
    no_ltr_list = get_documents_from_database(docs)
    return no_ltr_list


# LTR SEARCH RESULTS
def ltr_search_result_model1(query, rerank):

    qa_pos = words_to_pos_tags(query)
    qa_pos_bigram = string_to_bigrams(qa_pos)
    qa_pos_trigram = string_to_trigrams(qa_pos)
    qa_parse_tree = parse_tree_productions(query)

    payload = {
        "q": query,
        "defType": "edismax",
        "qf": "qa",
        "rq": f'{{!ltr model=lambdamart_model1 reRankDocs="{rerank}" \
            efi.q2="{qa_pos}" \
            efi.q3="{qa_pos_bigram}" \
            efi.q4="{qa_pos_trigram}" \
            efi.q5="{qa_parse_tree}"}}',
        "fl": "id",
        "rows": 1002,
    }

    docs = send_query_to_solr(payload)
    ltr_list = get_documents_from_database(docs)
    
    return ltr_list


def ltr_search_result_model2(query, n, q, a, rerank):

    ss = query
    ss_pos = words_to_pos_tags(ss)
    ss_pos_bigram = string_to_bigrams(ss_pos)
    ss_pos_trigram = string_to_trigrams(ss_pos)
    ss_parse_tree = parse_tree_productions(ss)

    before = n_words_before_answer(q,n)
    before_last = last_word_of_string(before)
    before_last_pos = words_to_pos_tags(before_last)
    before_pos = words_to_pos_tags(before)
    before_pos_bigram = string_to_bigrams(before_pos)
    before_pos_trigram = string_to_trigrams(before_pos)
    before_parse_tree = parse_tree_productions(before)

    after = n_words_after_answer(q,n)
    after_first = first_word_of_string(after)
    after_first_pos = words_to_pos_tags(after_first)
    after_pos = words_to_pos_tags(after)
    after_pos_bigram = string_to_bigrams(after_pos)
    after_pos_trigram = string_to_trigrams(after_pos)
    after_parse_tree = parse_tree_productions(after)

    ans_tags = words_to_pos_tags(a)
    ans = a
    ans_first = first_word_of_string(a)
    ans_last = last_word_of_string(a)
    ans_pos = concat_string_with_underscore(ans_tags)
    ans_first_pos = words_to_pos_tags(ans_first)
    ans_last_pos = words_to_pos_tags(ans_last)
    ans_is_first = answer_is_at_beginning_query(q)
    ans_is_last = answer_is_at_end_query(q)
    ans_length = string_length(a)

    payload = {
        "q": query,
        "defType": "edismax",
        "qf": "ss",
        "rq": f'{{!ltr model=lambdamart_model2 reRankDocs="{rerank}" \
            efi.q2="{ss_pos}" \
            efi.q3="{ss_pos_bigram}" \
            efi.q4="{ss_pos_trigram}" \
            efi.q5="{ss_parse_tree}" \
            efi.q6="{before}" \
            efi.q7="{before_last}" \
            efi.q8="{before_last_pos}" \
            efi.q9="{before_pos}" \
            efi.q10="{before_pos_bigram}" \
            efi.q11="{before_pos_trigram}" \
            efi.q12="{before_parse_tree}" \
            efi.q13="{after}" \
            efi.q14="{after_first}" \
            efi.q15="{after_first_pos}" \
            efi.q16="{after_pos}" \
            efi.q17="{after_pos_bigram}" \
            efi.q18="{after_pos_trigram}" \
            efi.q19="{after_parse_tree}" \
            efi.q20="{ans}" \
            efi.q21="{ans_first}" \
            efi.q22="{ans_last}" \
            efi.q23="{ans_pos}" \
            efi.q24="{ans_first_pos}" \
            efi.q25="{ans_last_pos}" \
            efi.q26="{ans_is_first}" \
            efi.q27="{ans_is_last}" \
            efi.q28="{ans_length}"}}',
        "fl": "id",
        "rows": 1002,
    }

    docs = send_query_to_solr(payload)
    ltr_list = get_documents_from_database(docs)

    return ltr_list


# ------------------------------------------------------------------------------
# QUIZ - MORE QUESTIONS LIKE THIS

def recommend_view(request, arg_question, arg_answer):

    # CHECK SOLR STATUS
    solr_down = check_solr_status()
    if solr_down == True:
        context = {'context_solr_down': solr_down}
        return render(request, 'search/search_recommend.html', context)

    # EXTRACT QUERY STRING (4 words before ans + ans + 4 words after ans)
    n = 4
    q = arg_question
    a = arg_answer
    substring = question_substring(q,a,n)
    query = substring
    arg_question_answer_space = arg_question.replace('*','____')

    # RETURN RESULTS FOR NO LTR
    no_ltr_list = no_ltr_search_result(query)

    # RETURN RESULTS FOR LTR (MODEL 2)
    rerank = 1002
    ltr_list = ltr_search_result_model2(query, n, q, a, rerank)

    result_ltr = ltr_list
    result = no_ltr_list

    result_count_ltr = len(ltr_list)
    result_count = len(no_ltr_list)

    no_result = False
    single_result = False

    no_result_ltr = False
    single_result_ltr = False

    if result_count==0:
        no_result = True

    if result_count_ltr==0:
        no_result==True

    if result_count == 1:
        single_result = True

    if result_count_ltr == 1:
        single_result_ltr = True

    top = 10
    top_ltr = 10

    context = { 'context_question': arg_question_answer_space,
                'context_answer': arg_answer,
                'context_substring': substring,

                'context_top': top,
                'context_top_ltr': top_ltr,

                'context_no_result': no_result,
                'context_single_result': single_result,
                'context_no_result_ltr': no_result_ltr,
                'context_single_result_ltr': single_result_ltr,

                'context_result_count': result_count,
                'context_result_count_ltr': result_count_ltr,

                'context_result': result,
                'context_result_ltr': result_ltr,
                'context_solr_down': solr_down,
    }
    return render(request, 'search/search_recommend.html', context)


#-------------------------------------------------------------------------------
# INTELLIGENT SEARCH PAGE

def ltrsearch_view(request):
    context = {}
    return render(request, "search/search_learntorank.html", context)


def ltrsearch_result_view(request):

    solr_down =  check_solr_status()
    if solr_down == True:
        context = {'context_solr_down': solr_down}
        return render(request, 'search/search_result_learntorank.html', context)

    # (3) GET INPUT
    query1 = request.GET.get('query_ltr1')    # model 1
    query2 = request.GET.get('query_ltr2')    # model 2
    top = request.GET.get('top')
    rerank = request.GET.get('rerank')

    # (4) VARIABLES
    q1 = False
    q2 = False
    substring = False
    answer =''

    # MODEL 2
    if query2:
        q2 = True
        n=4
        question = query2

        answer = re.search('\((.+?)\)',query2).group(1)   # answer without parentheses

        answer1 = '(' + answer + ')'
        q = query2.replace(answer1, '*') #

        substring = question_substring(q, answer, n)
        query = substring

        # MODEL 2 no LTR
        no_ltr_list = no_ltr_search_result(query)

        # MODEL 2 LTR
        ltr_list = ltr_search_result_model2(query, n, q, answer, rerank)

    # MODEL 1
    else:
        q1 = True
        question = query1
        query = query1.strip()

        # MODEL 1 no LTR
        no_ltr_list = no_ltr_search_result(query)

        # MODEL 1 LTR
        ltr_list = ltr_search_result_model1(query, rerank)

    result = no_ltr_list
    result_ltr = ltr_list

    result_count = len(no_ltr_list)
    result_count_ltr = len(ltr_list)

    no_result = False
    no_result_ltr = False

    single_result = False
    single_result_ltr = False

    use_bm25_result = False

    # NO LTR RESULTS
    if int(top) > result_count:
        top = result_count

    if result_count==0:
        no_result = True

    if result_count == 1:
        single_result = True

    # LTR RESULTS
    if result_count_ltr==0:
        if result_count==0:
            no_result_ltr = True
        else:
            use_bm25_result = True
            result_ltr = result
            result_count_ltr = result_count

    if int(top) > result_count_ltr:
        top_ltr = result_count_ltr
    else:
        top_ltr = top

    if result_count_ltr == 1:
        single_result_ltr = True

    if result_count_ltr==0:
        no_result==True

    #
    query_text = ""

    context = { 'context_query1': q1,
                'context_query2': q2,

                'context_question': question,
                'context_answer': answer,

                'context_query_text': query_text,
                'context_substring': substring,

                'context_top': top,
                'context_no_result': no_result,
                'context_single_result': single_result,
                'context_result': result,
                'context_result_count': result_count,

                'context_top_ltr': top_ltr,
                'context_no_result_ltr': no_result_ltr,
                'context_single_result_ltr': single_result_ltr,

                'context_result_ltr': result_ltr,
                'context_result_count_ltr': result_count_ltr,
                'context_use_bm25_result': use_bm25_result,
    }
    return render(request, 'search/search_result_learntorank.html', context)

#-------------------------------------------------------------------------------
# SEARCH PAGE
# Search link in base.html calls TopicView() to display this form and the entire search page

def TopicView(request):
    form = TopicForm()
    context = {'context_topic_form': form}
    return render(request, "search/search.html", context)


def searchtopic_view(request):
    form = TopicForm(request.GET)
    by_topic = False
    if form.is_valid():
        by_topic = True
        query = form.cleaned_data['qb_topic']
        result = ModelQuestionbank.objects.filter(qb_topic = query)

    result_count = result.count()
    no_result = False
    if not result:
        no_result = True

    context = {'context_no_result': no_result,
                'context_result': result,
                'context_result_count': result_count,
                'context_query_text': query,
                'context_search_by_topic': by_topic,
    }
    return render(request, 'search/search_result.html', context)


# - SOLR SEARCH (query1)
# - SEARCH BY QUESTION TEXT (query2)
# - SEARCH BY ANSWER CHOICE TEXT (query3)

def searchtext_view(request):

    query1 = request.GET.get('query_all')      # solr
    query2 = request.GET.get('query_question')
    query3 = request.GET.get('query_choice')

    top = request.GET.get('top')

    if not top:
        top = 0

    form = TopicForm(request.GET)
    if form.is_valid():
        query4 = form.cleaned_data['qb_topic']

    search_by_choice = False
    search_by_question = False
    search_by_all = False
    retrieve_all = False

    if query3:
        query3 = query3.strip()                 
        query_text = re.sub(' +', ' ', query3)  # reduce to single whitespace between words
        result = ModelQuestionbank.objects.filter(Q(qb_answer__icontains=query_text) |
                                                Q(qb_choice1__icontains=query_text) |
                                                Q(qb_choice2__icontains=query_text) |
                                                Q(qb_choice3__icontains=query_text) )
        search_by_choice = True

    elif query2:
        query2 = query2.strip()
        query_text = re.sub(' +', ' ', query2)
        result = ModelQuestionbank.objects.filter(Q(qb_question__icontains=query_text))
        search_by_question = True

    # solr
    elif query1:
        solr_down = check_solr_status()
        if solr_down == True:
            context = {'context_solr_down': solr_down}
            return render(request, 'search/search_result.html', context)

        query1 = query1.strip()
        result = no_ltr_search_result(query1)  # no_ltr_list
        query_text = query1

        search_by_all = True

    if query1:
        result_count = len(result)
    else:
        result_count = result.count()

    no_result = False
    single_result = False
    ten_result = False

    if int(top) > result_count:
        top = result_count

    if result_count==0:
        no_result = True

    if result_count == 1:
        single_result = True

    if result_count > 20:
        ten_result = True

    context = { 'context_search_by_choice': search_by_choice,
                'context_search_by_question': search_by_question,
                'context_search_by_all': search_by_all,
                'context_no_result': no_result,
                'context_single_result': single_result,
                'context_ten_result': ten_result,
                'context_result': result,
                'context_result_count': result_count,
                'context_query_text': query_text,
                'context_top': top,
                }
    return render(request, 'search/search_result.html', context)


#-------------------------------------------------------------------------------
# QUESTION DISPLAY WHEN USER SELECTS QUESTION FROM SEARCH RESULTS

def question_choices(q):
    """
    helper function for qbsession_view()
    """
    all_choices = [q.qb_answer, q.qb_choice1, q.qb_choice2, q.qb_choice3]
    shuffle(all_choices)
    return all_choices


def check_answer(question_answer, user_answer):
    """
    helper function for qbdisplay_view()
    """
    if user_answer == question_answer:
        return True
    else:
        return False


def qbsession_view(request, arg_question_id):
    """
    Called from qbdisplay_view() and qbresult_view()
    """
    question = ModelQuestionbank.objects.get(id = arg_question_id)

    try:
        del request.session['question']
        del request.session['user']
    except KeyError:
        pass

    request.session['question'] = {
        str(arg_question_id): { c : False for c in question_choices(question) if c != 'na'}
    }

    request.session['user'] = {}
    request.session.set_expiry(0)

    return redirect('appsearch:qbdisplayview', arg_question_id)


def qbdisplay_view(request, arg_question_id):
    if not request.session['question']:
        return redirect('appsearch:qbsessionview', arg_question_id)

    question = ModelQuestionbank.objects.get(id = arg_question_id)

    dict_choices = request.session['question'][str(arg_question_id)]
    list_choices = [ c for c in dict_choices ]

    context = {
        'context_topic'           : question.qb_topic,
        'context_question'        : question,
        'context_list_choices'    : list_choices,
    }

    if request.method == 'POST':
        request.session['question'][str(arg_question_id)].update(
                {c: True for c in list_choices if question.qb_answer == c}
        )

        question_choices = { c: true_or_false for c, true_or_false in request.session['question'][str(arg_question_id)].items() }

        request.session['user'].update( {
                str(arg_question_id) : {
                        'user' : {
                            'question_text'         : question.qb_question,
                            'question_choices'      : question_choices,
                            'user_answer_selected'  : request.POST.get(str(question.id)),
                            'user_answer_check'     : check_answer(question.qb_answer, request.POST.get(str(question.id))),
                    }
                }
        })
        request.session.modified = True
        return redirect('appsearch:qbresultview', arg_question_id)

    return render(request, 'search/qb_display.html', context)


def qbresult_view(request, arg_question_id):
    if not request.session['question']:
        return redirect('appsearch:qbsessionview', arg_question_id)

    question = ModelQuestionbank.objects.get(id = arg_question_id)
    dict_question = { str(arg_question_id) : request.session['user'][str(arg_question_id)]}.items()

    context = {
        'context_question' : question,
        'context_topic': question.qb_topic,
        'context_dict_question' : dict_question,
    }
    return render(request, 'search/qb_result.html', context)