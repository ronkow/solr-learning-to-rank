import os               # os.path.join
import pandas as pd

import nltk             #for POS tagging
from nltk.tree import *

from pycorenlp import StanfordCoreNLP
parser = StanfordCoreNLP('http://localhost:9000')  # for production rules


DATA_DIR = "data/"

DATA_DOC = os.path.join(DATA_DIR, "raw/rawdata_doc.csv")                                  # documents for training, validation, testing datasets
DATA_QUERY_TRAIN = os.path.join(DATA_DIR, "raw/rawdata_query.csv")                        # queries for training dataset
DATA_QUERY_VALIDATE_TEST = os.path.join(DATA_DIR, "raw/rawdata_query_validate_test.csv")  # queries for validation and testing datasets

FEATURE_DOC = os.path.join(DATA_DIR, "feature/feature_doc.csv")
FEATURE_QUERY_TRAIN = os.path.join(DATA_DIR, "feature/feature_query.csv")
FEATURE_QUERY_VALIDATE_TEST = os.path.join(DATA_DIR, "feature/feature_query_validate_test.csv")


# UTILITY FUNCTIONS

def csv_to_df(filepath):
    """
    Convert CSV file to dataframe
    Parameter: 
        filepath: path of csv file to be read
    Return: pandas dataframe
    """
    df1 = pd.read_csv(filepath)
    return df1


def df_to_csv(df, filepath):
    """
    Convert dataframe to CSV file
    Parameters:
        df: dataframe
        filepath: path of csv file to write to
    """
    df.to_csv(filepath, encoding='utf-8', index=False)
    
    
def convert_list_tuple_to_string(x):
    """
    Convert list or tuple to string
    Parameter: 
        x: list or tuple of words
    Return: string of words, separated by whitespace
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
    Concatenate tokens in a string with underscores
    Parameter: 
        s: string of words separated by whitespace
    Return: words concatenated with the underscore character
    """
    t = s.split()
    s1 = ''
    for w in t:
        if s1 == '':
            s1 = w
        else:
            s1 = s1 + '_' + w
    return s1        


# PARSE TREES

def parse_tree(s):
    """
    Generate constituency parse tree
    Parameter: 
        s: string
    Return: parse tree from Tree.fromstring()
    """
    output = parser.annotate( s, properties={'annotators': 'parse', 'outputFormat': 'json', 'timeout': 1000,} )
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
    Get production rules
    Parameter: 
        s: question, answer (strings)
    Return: a string of all productions (excluding the root and leaf nodes) in constituency parse tree of question, 
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


def print_parse_tree(s):
    """
    Print the constituency parse tree of a string
    Parameter: 
        s: string
    Return: the constituency parse tree
    Call:
        parse_tree(s)
    """
    t = parse_tree(s)    
    t.pretty_print()
    
    
def print_parse_tree_with_answer(q,a):
    """
    Print the constituency parse tree of a string (question and answer)
    Parameters: 
        q: question (string)
        a: answer (string)
    Return: constituency parse tree
    Call: 
        print_parse_tree()
    """
    q = q.replace("*", a)
    return print_parse_tree(q)


# POS TAGS

def words_to_pos_tags(s):
    """
    Convert words to POS tags
    Parameter: 
        s: string
    Return: POS tags (string) separated by whitespace
    """
    t = s.split()               
    word_tag = nltk.pos_tag(t)  # word_tag = [('He', 'PRP'), ...] 
    
    tags = ''
    for p in word_tag:          
        tag = p[1]              # tag = 'PRP'
        if tags == '':
            tags = tag
        else:
            tags = tags + ' ' + tag
    return tags    


# NGRAMS

def ngram_list_to_string(ngram_list):
    """
    Parameter: 
        ngram_list: list of bigrams or trigrams of words
    Return: string of bigrams or trigrams separated by whitespace
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
    Parameter: 
        s: string of words
    Return: string of bigrams of words, words concatenated by the underscore in each bigram
    """
    t = s.split()
    bigram_list = list(nltk.ngrams(t,2))  # list of tuples [('xxx','yyy'),...]
    return ngram_list_to_string(bigram_list)


def string_to_trigrams(s):
    """
    Parameter: 
        s: string of words
    Return: string of trigrams of words, words concatenated by the underscore in each trigram
    """
    t = s.split()
    trigram_list = list(nltk.ngrams(t,3))  # list of tuples [('xxx','yyy','zzz'),...]
    return ngram_list_to_string(trigram_list)


# DATA FIELDS

def question_complete(q,a):
    """
    Parameters: 
        q: question containing * (string)
        a: answer (strings)
    Return: the complete question in which * is replaced by the answer
    """
    return q.replace("*", a)


def n_words_before_answer(q,n):
    """
    Parameter: 
        q: question (string) containing the * character
        n: number of words before *
    Return: previous_word(string)
        Two words to the left of the * character.
        If * is the second word in the sentence, return one word.
        If * is the first word in the sentence, return empty string.
    """
    string_before = q.split('*')[0]                # split into two strings
    word_list = string_before.strip().split(' ')[-n:]
    return convert_list_tuple_to_string(word_list)


def n_words_after_answer(q,n):
    """
    Parameter: 
        q: question (string) containing the * character
        n: number of words after *
    Return: next_word(string)
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
    Parameter: 
        q: question containing * (string)
        a: answer (string)
        n: integer n (number of words before and after answer)
    Return: the string 'ppp aaa xxx', 
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
    Parameter: 
        s: string
    Return: last word in the string
    """
    if s:
        s1 = s.split()
        return s1[-1]
    else:
        return ''
    
    
def first_word_of_string(s):
    """
    Parameter: 
        s: string
    Return: first word in the string
    """
    if s:
        s1 = s.split()
        return s1[0]
    else:
        return ''
    
    
def answer_is_at_beginning_doc(q):
    """
    Parameter: 
        a: question (string) containing the * character
    Return: boolean 
        1 if * is at the start of the question
        0 otherwise
    """
    t = q.split(' ',1)[0]        
    if t == '*':
        return 'b'
    else:
        return 'x'

    
def answer_is_at_end_doc(q):
    """
    Parameter: 
        q: question(string) containing the * character
    Return: boolean 
        1 if * is at the end of the question
        0 otherwise
    """
    t = q.split('*')[1]              
    if t == '.' or t == '?' or t == '!':
        return 'e'
    else:
        return 'x' 
    
    
def answer_is_at_beginning_query(q):
    """
    Parameter: 
        q: question (string) containing the * character
    Return: boolean 
        1 if * is at the start of the question
        0 otherwise
    """
    t = q.split(' ',1)[0]        
    if t == '*':
        return 'b'
    else:
        return 'y'
    
    
def answer_is_at_end_query(q):
    """
    Parameter: 
        q: question(string) containing the * character
    Return: boolean 
        1 if * is at the end of the question
        0 otherwise
    """
    t = q.split('*')[1]              
    if t == '.' or t == '?' or t == '!':
        return 'e'
    else:
        return 'y'
    
    
def string_length(s):
    """
    Parameter: 
        s: sentence (string)
    Return: the number of words in the sentence (integer)
        * is counted as one word.
    """
    return len(s.split())


# GRAMMAR TOPICS

def id_to_topic_name(id):
    """
    Convert topic id to topic name
    Parameter: 
        id: topic id
    Return: topic name
    """
    if id == 1:
        return 'prepositions'
    elif id == 2:
        return 'conjunctions'
    elif id == 3:
        return 'phrasal verbs'
    elif id == 4:
        return 'verb tenses'
    else:
        return 'pronouns'
    
    
def add_topic_name(df):
    """
    Parameter: 
        df: dataframe
    Return: dataframe with features 
    """    
    for i, row in df.iterrows(): 
        id = row['qb_topic_id']
        name = id_to_topic_name(id)
        
        df.loc[i,'topic'] = name        
    return df    


# DATAFRAMES FOR FEATURES

# MODEL 1 FEATURES

def create_features_df_model1(df):
    """
    Parameter: 
        df: dataframe
    Return: dataframe with features 
    """    
    for i, row in df.iterrows(): 
        q = row['qb_question']
        a = row['qb_answer']
        qa = question_complete(q,a)
        qa_tags = words_to_pos_tags(qa)
        
        df.loc[i,'qa'] = qa             # for baseline BM25 ranking in Model 1       
        df.loc[i,'qa_pos'] = qa_tags
        df.loc[i,'qa_pos_bigram'] = string_to_bigrams(qa_tags) 
        df.loc[i,'qa_pos_trigram'] = string_to_trigrams(qa_tags)
        df.loc[i,'qa_parse_tree'] = parse_tree_productions(qa)        
        
    return df    


# MODEL 2 FEATURES

def create_features_df_model2(df, data_type):
    """
    Create the dataframe of query or document features
    Parameter: 
        df: dataframe
        data_type: one of the following strings:
            query, doc
    Return: dataframe with features 
    """ 
    n = 4
    for i, row in df.iterrows(): 
        q = row['qb_question']
        a = row['qb_answer']
        substr = question_substring(q,a,n)
        substr_tags = words_to_pos_tags(substr)
        
        # FIELD: substring
        df.loc[i,'ss'] = substr             # for baseline BM25 ranking in Model 2       
        df.loc[i,'ss_pos'] = substr_tags
        df.loc[i,'ss_pos_bigram'] = string_to_bigrams(substr_tags) 
        df.loc[i,'ss_pos_trigram'] = string_to_trigrams(substr_tags)
        df.loc[i,'ss_parse_tree'] = parse_tree_productions(substr)        
        
        # FIELD: words before answer
        before = n_words_before_answer(q,n)
        before_tags = words_to_pos_tags(before)
        last = last_word_of_string(before) 
        last_tag = words_to_pos_tags(last)

        df.loc[i,'before'] = before 
        df.loc[i,'before_last'] = last
        df.loc[i,'before_last_pos'] = last_tag
        df.loc[i,'before_pos'] = before_tags
        df.loc[i,'before_pos_bigram'] = string_to_bigrams(before_tags)
        df.loc[i,'before_pos_trigram'] = string_to_trigrams(before_tags)
        df.loc[i,'before_parse_tree'] = parse_tree_productions(before)
        
        # FIELD: words after answer
        after = n_words_after_answer(q,n)
        after_tags = words_to_pos_tags(after)
        first = first_word_of_string(after) 
        first_tag = words_to_pos_tags(first)

        df.loc[i,'after'] = after 
        df.loc[i,'after_first'] = first
        df.loc[i,'after_first_pos'] = first_tag
        df.loc[i,'after_pos'] = after_tags
        df.loc[i,'after_pos_bigram'] = string_to_bigrams(after_tags)
        df.loc[i,'after_pos_trigram'] = string_to_trigrams(after_tags)
        df.loc[i,'after_parse_tree'] = parse_tree_productions(after)
        
        # FIELD: answer        
        ans_tags = words_to_pos_tags(a)
        ans_first = first_word_of_string(a) 
        ans_last = last_word_of_string(a)

        df.loc[i,'ans'] = a
        df.loc[i,'ans_first'] = ans_first
        df.loc[i,'ans_last'] = ans_last
        df.loc[i,'ans_pos'] = concat_string_with_underscore(ans_tags)
        df.loc[i,'ans_first_pos'] = words_to_pos_tags(ans_first) 
        df.loc[i,'ans_last_pos'] = words_to_pos_tags(ans_last) 
        
        if data_type == 'doc':
            df.loc[i,'ans_is_first'] = answer_is_at_beginning_doc(q) 
            df.loc[i,'ans_is_last'] = answer_is_at_end_doc(q) 
        elif data_type == 'query':
            df.loc[i,'ans_is_first'] = answer_is_at_beginning_query(q)
            df.loc[i,'ans_is_last'] = answer_is_at_end_query(q)
        df.loc[i,'ans_length'] = string_length(a) 

    return df    


def main():
    df_data_doc = csv_to_df(DATA_DOC)
    df_data_query_train = csv_to_df(DATA_QUERY_TRAIN)
    df_data_query_validate_test = csv_to_df(DATA_QUERY_VALIDATE_TEST)
    
    
    # DOCUMENT FEATURES

    df_doc = add_topic_name(df_data_doc)
    df_doc = create_features_df_model1(df_data_doc)
    df_features_doc = create_features_df_model2(df_doc, 'doc')
    
    # QUERY FEATURES (TRAIN)

    df_query1 = add_topic_name(df_data_query_train)
    df_query1 = create_features_df_model1(df_data_query_train)
    df_features_query_train = create_features_df_model2(df_query1, 'query')
    
    # QUERY FEATURES (VALIDATION, TESTING)

    df_query2 = add_topic_name(df_data_query_validate_test)
    df_query2 = create_features_df_model1(df_data_query_validate_test)
    df_features_query_validate_test = create_features_df_model2(df_query2, 'query')
    
    # SAVE DATA
    
    df_to_csv(df_features_doc, FEATURE_DOC)
    df_to_csv(df_features_query_train, FEATURE_QUERY_TRAIN)
    df_to_csv(df_features_query_validate_test, FEATURE_QUERY_VALIDATE_TEST)
    
    
if __name__ == '__main__':
    main()