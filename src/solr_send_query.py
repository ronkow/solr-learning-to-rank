# SENDING QUERIES TO SOLR TO COMPARE SEARCH RESULTS

import random    
import os        
import csv       
import json      
import requests  
import urllib    

DATA_DIR  = "data/"
FEATURE_QUERY_VALIDATE_TEST = os.path.join(DATA_DIR, "feature/feature_query_validate_test.csv")

SOLR_URL = "http://localhost:8983/solr/core1"

N = 10    # Top N results to display


def select_random_query(myseed):
    """
    Select a random query from the query/validation dataset
    Parameter:
        myseed: seed value
    """
    with open(FEATURE_QUERY_VALIDATE_TEST) as f:
        QUERY_LIST = [ {k: v for k, v in row.items()} for row in csv.DictReader(f, skipinitialspace=True) ]
    
    random.seed(myseed)
    random.shuffle(QUERY_LIST)
       
    query = QUERY_LIST[0]  
    
    return query   


def render_results(docs, query, ans, topic, top_n):

    print(f"Top {top_n} results for the query: {query} (answer: {ans}, topic: {topic})\n")
    
    for doc in docs:
        doc_id = int(doc["id"])
        qb_question = doc["qb_question"][0]     # solr indexed the data as a list! Can this be changed?
        qb_answer = doc["qb_answer"][0]
        qb_topic_id = doc["qb_topic_id"][0]
        print(f"doc_id: {doc_id} \t {qb_question} ({qb_answer})(topic: {qb_topic_id})")
        
    
def query_solr(payload):
    
    params = urllib.parse.urlencode(payload, quote_via=urllib.parse.quote_plus)
    search_url = SOLR_URL + "/query?" + params
    resp = requests.get(search_url)
    resp_json = json.loads(resp.text)
    docs = resp_json["response"]["docs"]
    
    return docs


# QUERY to SOLR BY DEFAULT BM25 (ENTIRE SENTENCE or SUBSTRING)
# NO MODEL: Default Solr (entire sentence)

def run_query_default_qa(q):
       
    ans = q['qb_answer']
    topic = q['qb_topic_id']
    query = q['qa']
    
    payload = {
        "q": query,
        "defType": "edismax",
        "qf": "qa",          # for dismax query parser 
        #"df": "qa",         # for standard query parser
        "fl": "id, qb_question, qb_answer, qb_topic_id",            
        "rows": N        
        
        # OPTIONAL PARAMS
        #"sort": "score desc",
        #"start": 0,
        #"fq":
        #"debug": "all",
        #"omitHeader": "false",
        #"explainOther": "",
        #"segmentTerminateEarly": "false",
        #"omitHeader": "false",
        #"echoParams": "explicit",
        #"timeAllowed": 1000000,
        #"wt": "json",
        #"indent": "true",
    }

    docs = query_solr(payload)
    print("QUERY: ENTIRE SENTENCE, ANSWER NOT INDICATED\n")
    print("Default Solr results:")
    return render_results(docs, query, ans, topic, N)


# NO MODEL: Default Solr (substring)

def run_query_default_ss(q):
       
    ans = q['qb_answer']
    topic = q['qb_topic_id']
    query = q['ss']
    
    payload = {
        "q": query,
        "defType": "edismax",
        "qf": "ss",
        "fl": "id, qb_question, qb_answer, qb_topic_id",            
        "rows": N
    }

    docs = query_solr(payload)
    print("QUERY: SUBSTRING, ANSWER INDICATED\n")
    print("Default Solr results:")
    return render_results(docs, query, ans, topic, N)


# QUERY to SOLR USING BASELINE MODELS
# Baseline models only have one feature: BM25 for entire sentence (Model 1) or BM25 for substring (Model 2)

# When we enable LTR, Solr will rerank the original results from default BM25 (i.e., when no ranking models are used)

# with LTR BASELINE MODEL 1 (entire sentence)

def run_query_lambdamart_baseline_model1(q):
    
    ans = q['qb_answer']
    topic = q['qb_topic_id']
    query = q['qa']

    payload = {
        "q": query,
        "defType": "edismax",
        "qf": "qa",
        "rq": f'{{!ltr model=lambdamart_model1_baseline reRankDocs=1002}}',
        "fl": "id, qb_question, qb_answer, qb_topic_id",            
        "rows": N
    }

    docs = query_solr(payload)
    print("LTR Baseline Model 1 results:")
    return render_results(docs, query, ans, topic, N)


# with LTR BASELINE MODEL 2 (substring)

def run_query_lambdamart_baseline_model2(q):
    
    ans = q['qb_answer']
    topic = q['qb_topic_id']
    query = q['ss']

    payload = {
        "q": query,
        "defType": "edismax",
        "qf": "ss",
        "rq": f'{{!ltr model=lambdamart_model2_baseline reRankDocs=1002}}',
        "fl": "id, qb_question, qb_answer, qb_topic_id",            
        "rows": N
    }

    docs = query_solr(payload)
    print("LTR Baseline Model 2 results:")
    return render_results(docs, query, ans, topic, N)


# QUERY to SOLR USING MODELS 1 AND 2

# with LTR MODEL 1

def run_query_lambdamart_model1(q):

    ans = q['qb_answer']
    topic = q['qb_topic_id']
    query = q['qa']
    
    f2 = q["qa_pos"]
    f3 = q["qa_pos_bigram"]
    f4 = q["qa_pos_trigram"]
    f5 = q["qa_parse_tree"]
    
    payload = {
        "q": query,
        "defType": "edismax",
        "qf": "qa",
        "rq": f'{{!ltr model=lambdamart_model1  reRankDocs=1002 \
            efi.q2="{f2}" \
            efi.q3="{f3}" \
            efi.q4="{f4}" \
            efi.q5="{f5}"}}',
        "fl": "id, qb_question, qb_answer, qb_topic_id",            
        "rows": N
    }

    docs = query_solr(payload)
    print("LTR Model 1 results:")
    return render_results(docs, query, ans, topic, N)


# with LTR MODEL 2

def run_query_lambdamart_model2(q):
    
    ans = q['qb_answer']
    topic = q['qb_topic_id']
    query = q['ss']
    
    f2 = q["ss_pos"]
    f3 = q["ss_pos_bigram"]
    f4 = q["ss_pos_trigram"]
    f5 = q["ss_parse_tree"]
    f6 = q["before"]
    f7 = q["before_last"]
    f8 = (q["before_last_pos"]).lower()
    f9 = q["before_pos"]
    f10 = q["before_pos_bigram"]
    f11 = q["before_pos_trigram"]
    f12 = q["before_parse_tree"]
    f13 = q["after"]
    f14 = q["after_first"]
    f15 = (q["after_first_pos"]).lower()
    f16 = q["after_pos"]
    f17 = q["after_pos_bigram"]
    f18 = q["after_pos_trigram"]
    f19 = q["after_parse_tree"]
    f20 = q["ans"]
    f21 = q["ans_first"]
    f22 = q["ans_last"]
    f23 = (q["ans_pos"]).lower()
    f24 = (q["ans_first_pos"]).lower()
    f25 = (q["ans_last_pos"]).lower()
    f26 = q["ans_is_first"]
    f27 = q["ans_is_last"]
    f28 = q["ans_length"]
    
    payload = {
        "q": query,
        "defType": "edismax",
        "qf": "ss",
        "rq": f'{{!ltr model=lambdamart_model2  reRankDocs=1002 \
            efi.q2="{f2}" \
            efi.q3="{f3}" \
            efi.q4="{f4}" \
            efi.q5="{f5}" \
            efi.q6="{f6}" \
            efi.q7="{f7}" \
            efi.q8="{f8}" \
            efi.q9="{f9}" \
            efi.q10="{f10}" \
            efi.q11="{f11}" \
            efi.q12="{f12}" \
            efi.q13="{f13}" \
            efi.q14="{f14}" \
            efi.q15="{f15}" \
            efi.q16="{f16}" \
            efi.q17="{f17}" \
            efi.q18="{f18}" \
            efi.q19="{f19}" \
            efi.q20="{f20}" \
            efi.q21="{f21}" \
            efi.q22="{f22}" \
            efi.q23="{f23}" \
            efi.q24="{f24}" \
            efi.q25="{f25}" \
            efi.q26="{f26}" \
            efi.q27="{f27}" \
            efi.q28="{f28}"}}',
        "fl": "id, qb_question, qb_answer, qb_topic_id",            
        "rows": N,
    }
    
    docs = query_solr(payload)
    print("LTR Model 2 results:")
    return render_results(docs, query, ans, topic, N)


def main():
    query = select_random_query(8)

    run_query_default_qa(query)
    print()
    run_query_lambdamart_baseline_model1(query)
    print()
    run_query_lambdamart_model1(query)
    print()

    run_query_default_ss(query)
    print()
    run_query_lambdamart_baseline_model2(query)
    print()
    run_query_lambdamart_model2(query)


if __name__ == '__main__':
    main()