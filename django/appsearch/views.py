from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render, redirect
from django.views.generic import ListView, TemplateView
from django.db.models import Q

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import ModelQuestionbank
from .forms import TopicForm, ResultForm

from random import shuffle
from haystack.query import SearchQuerySet

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
import nltk             #for POS tagging

nltk_downloader = nltk.downloader.Downloader()

if not nltk_downloader.is_installed('punkt'):
    nltk_downloader.download('punkt')
if not nltk_downloader.is_installed('averaged_perceptron_tagger'):
    nltk_downloader.download('averaged_perceptron_tagger')

from nltk.tree import *
from stanza.server import CoreNLPClient

# ------------------------------------------------------------------------------
client = CoreNLPClient(
    memory='4G',
    endpoint='http://198.100.45.97:9000',
    be_quiet=True,
    start_server='DONT_START'
)
client.start()
import time
time.sleep(10)

def parse_tree(s):
    """
    argument: string
    return: parse tree from Tree.fromstring()
    """
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
    """
    arguments: question, answer (strings)
    return: a string of all productions (excluding the root and leaf nodes) in constituency parse tree of question,
    POS tags in each production concatenated by underscore character
    """
    t1 = parse_tree(s)
    if t1:
        t2 = t1.productions()
    else:
        return ''
    t3 = []
    productions = ''
    for x in t2:
        if "'" in str(x) or "ROOT" in str(x):  # leave out productions with root and leaf nodes
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

# ------------------------------------------------------------------------------
def convert_list_tuple_to_string(x):
    """
    argument: list or tuple of words
    return: string of words, separated by whitespace
    """
    s = ''
    for w in x:
        if s == '':
            s = w
        else:
            s = s + ' ' + w
    return s

def concat_string_with_underscore(s):
    """
    argument: string of words separated by whitespace
    return: words concatenated with the underscore character
    """
    t = s.split()
    s1 = ''
    for w in t:
        if s1 == '':
            s1 = w
        else:
            s1 = s1 + '_' + w
    return s1

def words_to_pos_tags(s):
    """
    argument: string
    return: POS tags (string) separated by whitespace
    """
    t = s.split()               # split into tokens
    word_tag = nltk.pos_tag(t)  # word_tag = [('He', 'PRP'), ...]

    tags = ''
    for p in word_tag:
        tag = p[1]              # tag = 'PRP'
        if tags == '':
            tags = tag
        else:
            tags = tags + ' ' + tag
    return tags

def ngram_list_to_string(ngram_list):
    """
    argument: list of bigrams or trigrams of words
    return: string of bigrams or trigrams separated by whitespace
    """
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
    """
    argument: string of words
    return: string of bigrams of words, words concatenated by the underscore in each bigram
    """
    t = s.split()
    bigram_list = list(nltk.ngrams(t,2))  # list of tuples [('xxx','yyy'),...]
    return ngram_list_to_string(bigram_list)

def string_to_trigrams(s):
    """
    argument: string of words
    return: string of trigrams of words, words concatenated by the underscore in each trigram
    """
    t = s.split()
    trigram_list = list(nltk.ngrams(t,3))  # list of tuples [('xxx','yyy','zzz'),...]
    return ngram_list_to_string(trigram_list)

def question_complete(q,a):
    """
    argument: question containing *, answer (strings)
    return: the complete question in which * is replaced by the answer
    """
    return q.replace("*", a)

def n_words_before_answer(q,n):
    """
    argument: question (string) containing the * character
    return: previous_word(string)
        Two words to the left of the * character.
        If * is the second word in the sentence, return one word.
        If * is the first word in the sentence, return empty string.
    """
    string_before = q.split('*')[0]                # split into two strings
    word_list = string_before.strip().split(' ')[-n:]
    return convert_list_tuple_to_string(word_list)

def n_words_after_answer(q,n):
    """
    argument: question (string) containing the * character
    return: next_word(string)
        Two words to the right of the * character.
        If * is the second last word, return the last word, excluding punctuation.
        If * is the last word, return empty string.
    """
    if q.endswith('*') or q == '':
        return ''
    else:
        string_after = q.split('*')[1]               # split into two strings
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
    """
    argument: question containing *, answer (strings), integer n (number of words before and after answer)
    return: the string 'ppp aaa xxx',
        where
        ppp are the n words before the answer
        aaa is the answer
        xxx are the n words after the answer
    """
    s1 = n_words_before_answer(q,n)
    s2 = n_words_after_answer(q,n)
    return (s1 + ' ' + a + ' ' + s2).strip()    # remove any white space at the start and end of string

def last_word_of_string(s):
    """
    argument: string
    returns: last word in the string
    """
    if s:
        s1 = s.split()
        return s1[-1]
    else:
        return ''

def first_word_of_string(s):
    """
    argument: string
    returns: first word in the string
    """
    if s:
        s1 = s.split()
        return s1[0]
    else:
        return ''

def answer_is_at_beginning_doc(q):
    """
    argument: question (string) containing the * character
    return: boolean
        1 if * is at the start of the question
        0 otherwise
    """
    t = q.split(' ',1)[0]        # split into tokens
    if t == '*':
        return 'b'
    else:
        return 'x'

def answer_is_at_end_doc(q):
    """
    argument: question(string) containing the * character
    return: boolean
        1 if * is at the end of the question
        0 otherwise
    """
    t = q.split('*')[1]              # split into tokens
    if t == '.' or t == '?' or t == '!':
        return 'e'
    else:
        return 'x'

def answer_is_at_beginning_query(q):
    """
    argument: question (string) containing the * character
    return: boolean
        1 if * is at the start of the question
        0 otherwise
    """
    t = q.split(' ',1)[0]        # split into tokens
    if t == '*':
        return 'b'
    else:
        return 'y'

def answer_is_at_end_query(q):
    """
    argument: question(string) containing the * character
    return: boolean
        1 if * is at the end of the question
        0 otherwise
    """
    t = q.split('*')[1]              # split into tokens
    if t == '.' or t == '?' or t == '!':
        return 'e'
    else:
        return 'y'

def string_length(s):
    """
    argument: sentence (string)
    return: the number of words in the sentence (integer)
        * is counted as one word.
    """
    return len(s.split())

# ------------------------------------------------------------------------------
def DataView(request):
    context = {}
    return render(request, "data/data.html", context)


def DataListView(request, arg_topic_id):
    if arg_topic_id==1:
        topic = 'prepositions'
    elif arg_topic_id==2:
        topic = 'conjunctions'
    elif arg_topic_id==3:
        topic = 'phrasal verbs'
    elif arg_topic_id==4:
        topic = 'verb tenses'
    else:
        topic = 'pronouns'

    result = ModelQuestionbank.objects.filter(qb_topic = arg_topic_id)
    result_count = result.count()
    no_result = False
    if not result:
        no_result = True

    context = {
        'context_no_result': no_result,
        'context_result': result,
        'context_result_count': result_count,
        'context_topic': topic,
    }
    return render(request, 'data/data_list.html', context)


def ltrsearch_view(request):
    context = {}
    return render(request, "search/search_learntorank.html", context)

# solr
def ltrsearch_result_view(request):
    SOLR_URL = "http://testuser:testpassword@198.100.45.97:8983/solr/qcore"

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    solr = sock.connect_ex(('198.100.45.97', 8983))

    if solr != 0:
        solr_down=True
        context = {'context_solr_down': solr_down}
        return render(request, 'search/search_result_learntorank.html', context)
    else:
        solr_down=False

    query1 = request.GET.get('query_ltr1')    # model 1
    query2 = request.GET.get('query_ltr2')    # model 2
    top = request.GET.get('top')

    q1 = False
    q2 = False
    substring = False
    answer =''
    ltr_list = []

    if query2:
        n=4
        question = query2.replace('(', '')
        question = question.replace(')', '')

        answer = re.search('\((.+?)\)',query2).group(1)   # return answer without parentheses
        answer1 = '(' + answer + ')'

        q = query2.replace(answer1, '*')
        substring = question_substring(q,answer,n)        # 4 word context
        query_text = substring.split()  # list of words

        # NO LTR
        result = SearchQuerySet().models(ModelQuestionbank)

        for w in query_text:
            result = result.filter_or(content=w)
            result = result.filter_or(content_auto=w)
        q2 = True

        # LTR
        a = answer

        # FIELD: substring
        ss = substring             # for baseline BM25 ranking in Model 2
        ss_pos = words_to_pos_tags(substring)
        ss_pos_bigram = string_to_bigrams(ss_pos)
        ss_pos_trigram = string_to_trigrams(ss_pos)
        ss_parse_tree = parse_tree_productions(substring)

        # FIELD: words before answer
        before = n_words_before_answer(q,n)
        before_last = last_word_of_string(before)
        before_last_pos = words_to_pos_tags(before_last)
        before_pos = words_to_pos_tags(before)
        before_pos_bigram = string_to_bigrams(before_pos)
        before_pos_trigram = string_to_trigrams(before_pos)
        before_parse_tree = parse_tree_productions(before)

        # FIELD: words after answer
        after = n_words_after_answer(q,n)
        after_first = first_word_of_string(after)
        after_first_pos = words_to_pos_tags(after_first)
        after_pos = words_to_pos_tags(after)
        after_pos_bigram = string_to_bigrams(after_pos)
        after_pos_trigram = string_to_trigrams(after_pos)
        after_parse_tree = parse_tree_productions(after)

        # FIELD: answer
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

        query = ss
        payload = {
            "q": query,
            "defType": "edismax",
            "qf": "ss",
            "rq": f'{{!ltr model=lambdamart_model2 \
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

        params = urllib.parse.urlencode(payload, quote_via=urllib.parse.quote_plus)
        search_url = SOLR_URL + "/query?" + params
        resp = requests.get(search_url)
        resp_json = json.loads(resp.text)
        docs = resp_json["response"]["docs"]

        for doc in docs:
            doc_id = int(doc["id"])
            q = ModelQuestionbank.objects.get(id = doc_id)
            ltr_list.append(q)

        result_ltr = ltr_list

    else:
        question = query1.replace('(', '')
        question = question.replace(')', '')

        query = question.strip()
        query_text = query.split()  # list of words

        # NO LTR
        result = SearchQuerySet().models(ModelQuestionbank)

        for w in query_text:
            result = result.filter_or(content=w)
            result = result.filter_or(content_auto=w)
        q1 = True

        # LTR
        qa_pos = words_to_pos_tags(query)
        qa_pos_bigram = string_to_bigrams(qa_pos)
        qa_pos_trigram = string_to_trigrams(qa_pos)
        qa_parse_tree = parse_tree_productions(query)

        payload = {
            "q": query,
            "defType": "edismax",
            "qf": "qa",
            "rq": f'{{!ltr model=lambdamart_model1 \
            efi.q2="{qa_pos}" \
            efi.q3="{qa_pos_bigram}" \
            efi.q4="{qa_pos_trigram}" \
            efi.q5="{qa_parse_tree}"}}',
            "fl": "id",
            "rows": 1002,
        }

        params = urllib.parse.urlencode(payload, quote_via=urllib.parse.quote_plus)
        search_url = SOLR_URL + "/query?" + params
        resp = requests.get(search_url)
        resp_json = json.loads(resp.text)
        docs = resp_json["response"]["docs"]

        for doc in docs:
            doc_id = int(doc["id"])
            q = ModelQuestionbank.objects.get(id = doc_id)
            ltr_list.append(q)

    # NO LTR RESULTS
    result_count = result.count()
    no_result = False
    single_result = False

    if int(top) > result_count:
        top = result_count

    if result_count==0:
        no_result = True

    if result_count == 1:
        single_result = True

    # LTR RESULTS
    result_ltr = ltr_list
    result_count_ltr = len(ltr_list)
    no_result_ltr = False
    single_result_ltr = False
    use_bm25_result = False

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

    context = {
        'context_query1': q1,
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


def searchtext_view(request):
    query1 = request.GET.get('query_choice')
    query2 = request.GET.get('query_question')
    query3 = request.GET.get('query_all')      # solr
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

    if query1:
        query1 = query1.strip()             # remove leading and trailing whitespace
        query_text = re.sub(' +', ' ', query1)  # reduce to single whitespace between words
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
    elif query3:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        solr = sock.connect_ex(('198.100.45.97', 8983))

        if solr != 0:
            solr_down=True
            context = {'context_solr_down': solr_down}
            return render(request, 'search/search_result.html', context)
        else:
            solr_down=False

        query3     = query3.strip()
        query_list = query3.split()    # list of words

        result = SearchQuerySet().models(ModelQuestionbank)
        query_text = ''

        for w in query_list:
            result = result.filter_or(content=w)
            result = result.filter_or(content_auto=w)
            query_text = query_text + ' ' + w

        query_text = query_text.strip()
        search_by_all = True

        # WORKS BUT NO OR
        # result = SearchQuerySet().models(ModelQuestionbank)
        # r1 = result.filter_or(content_auto=query_text)
        # r2 = result.filter_or(content=query_text)
        # result = r1 | r2

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

    context = {
        'context_search_by_choice': search_by_choice,
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


# Search link in base.html calls TopicView() to display this form and other search forms
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

    context = {
        'context_no_result': no_result,
        'context_result': result,
        'context_result_count': result_count,
        'context_query_text': query,
        'context_search_by_topic': by_topic,
    }
    return render(request, 'search/search_result.html', context)


# helper function for qbsession_view()
def question_choices(q):
    all_choices = [q.qb_answer, q.qb_choice1, q.qb_choice2, q.qb_choice3]
    shuffle(all_choices)
    return all_choices

# helper function for qbdisplay_view()
def check_answer(question_answer, user_answer):
    if user_answer == question_answer:
        return True
    else:
        return False


def qbsession_view(request, arg_question_id):
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
