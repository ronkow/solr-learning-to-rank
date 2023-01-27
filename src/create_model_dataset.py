# FEATURE VALUE EXTRACTION (BY SOLR) AND ADDING RELEVANCE LABELS TO DATASETS

import random    # random.randint
import os        # os.path.join
import csv       # csv.DictReader
import json      # json.dumps
import requests  # requests.post
import urllib    # urllib.parse.urlencode, urllib.parse.quote_plus
import re        # re.match
import solr

DATA_DIR   = "data/"

FEATURE_QUERY_TRAIN = os.path.join(DATA_DIR, "feature/feature_query.csv")
FEATURE_QUERY_VALIDATE_TEST = os.path.join(DATA_DIR, "feature/feature_query_validate_test.csv")

FEATURE_FILE_TEMPLATE_MODEL1 = os.path.join(DATA_DIR, "model/no_relevance_model1_{:s}.txt")
FEATURE_FILE_TEMPLATE_MODEL2 = os.path.join(DATA_DIR, "model/no_relevance_model2_{:s}.txt")


FILE_MODEL1_NO_RELEVANCE_TRAIN    = os.path.join(DATA_DIR, "model/no_relevance_model1_train.txt")
FILE_MODEL1_NO_RELEVANCE_VALIDATE = os.path.join(DATA_DIR, "model/no_relevance_model1_validate.txt")
FILE_MODEL1_NO_RELEVANCE_TEST     = os.path.join(DATA_DIR, "model/no_relevance_model1_test.txt")

FILE_MODEL2_NO_RELEVANCE_TRAIN    = os.path.join(DATA_DIR, "model/no_relevance_model2_train.txt")
FILE_MODEL2_NO_RELEVANCE_VALIDATE = os.path.join(DATA_DIR, "model/no_relevance_model2_validate.txt")
FILE_MODEL2_NO_RELEVANCE_TEST     = os.path.join(DATA_DIR, "model/no_relevance_model2_test.txt")


FILE_MODEL1_TRAIN    = os.path.join(DATA_DIR, "model/model1_train.txt")
FILE_MODEL1_VALIDATE = os.path.join(DATA_DIR, "model/model1_validate.txt")
FILE_MODEL1_TEST     = os.path.join(DATA_DIR, "model/model1_test.txt")

FILE_MODEL2_TRAIN    = os.path.join(DATA_DIR, "model/model2_train.txt")
FILE_MODEL2_VALIDATE = os.path.join(DATA_DIR, "model/model2_validate.txt")
FILE_MODEL2_TEST     = os.path.join(DATA_DIR, "model/model2_test.txt")

SOLR_URL = "http://localhost:8983/solr/core1"

FEAT_SUFFIXES = ["train", "validate", "test"]


# CREATE DATASETS in LETOR FORMAT for MODELS 1 AND 2

def format_letor(qid, feat_string, docid, FEATURE_LIST):
    """
    Format a row in the input dataset
    Parameters:
        qid: id of query
        feat_string: feature ids and values
        docid: id of document
        FEATURE_LIST: list of feature names
    Return:
       A string of the following format:
           qid:xxx feature_id1:feature_value1 feature_id2: feature_value2... # docid:yyy
    """
    feat_pairs = []
    feature_name_to_id = {name: idx + 1 for idx, name in enumerate(FEATURE_LIST)}
    
    for feat_nv in feat_string.split(','):
        feat_name, feat_value = feat_nv.split('=')
        
        feat_id = str(feature_name_to_id[feat_name])
               
        feat_value = float(feat_value)
        feat_value = str(feat_value)
        
        feat_pairs.append( ':'.join([feat_id, feat_value]) )

    return f"qid:{qid} {' '.join(feat_pairs)} # docid:{docid}"


def create_query_lists():
    """
    Convert the CSV files for queries (training, validation/testing) into lists
    Split the validation/testing lists into separate validation and test queries
    Return:
        train_q: list of queries for training
        validate_q: list of queries for validation
        test_q: list of queries for testing
    """
    with open(FEATURE_QUERY_TRAIN) as f1:
        QUERY_LIST_TRAIN = [ {k: v for k, v in row.items()} for row in csv.DictReader(f1, skipinitialspace=True) ]

    with open(FEATURE_QUERY_VALIDATE_TEST) as f2:
        QUERY_LIST_VALIDATE_TEST = [ {k: v for k, v in row.items()} for row in csv.DictReader(f2, skipinitialspace=True) ]
    
    random.seed(1)
    random.shuffle(QUERY_LIST_VALIDATE_TEST)
       
    train_q    = QUERY_LIST_TRAIN
    validate_q = QUERY_LIST_VALIDATE_TEST[0:75]
    test_q     = QUERY_LIST_VALIDATE_TEST[75:]
    
    return train_q, validate_q, test_q


def query_solr(payload):
    """
    Send the payload to Solr
    Parameter:
        payload: payload in JSON format
    Return:
        docs: response containing document ids, feature values
    """
    params = urllib.parse.urlencode(payload, quote_via=urllib.parse.quote_plus)
    search_url = SOLR_URL + "/query?" + params
    resp = requests.get(search_url)
    resp_json = json.loads(resp.text)
    docs = resp_json["response"]["docs"]
    
    return docs


def create_model1_data(FEATURE_LIST, train_q, validate_q, test_q):
    """
    Create the payload in JSON format for Model 1 to be sent to Solr
    Formats the response in LETOR dataset format
    Paramaters:
        FEATURE_LIST: list of feature names
        train_q: list of queries for training
        validation_q: list of queries for validation
        test_q: list of queries for testing
    Calls:
        query_solr(payload)
        format_letor(qid, feat_string, docid, FEATURE_LIST)
    """
    qid = 1
    for i, queries in enumerate([train_q, validate_q, test_q]):    #[(0,'train_q'), (1,'validate_q'), (2,'test_q')]
    
        model_data_file = open(FEATURE_FILE_TEMPLATE_MODEL1.format(FEAT_SUFFIXES[i]), "w")

        for q in queries:
            f1 = q["qa"]
            f2 = q["qa_pos"]
            f3 = q["qa_pos_bigram"]
            f4 = q["qa_pos_trigram"]
            f5 = q["qa_parse_tree"]
                          
            payload = {
                "q": f1,
                "defType": "edismax",
                "qf": "qa",
                "rq": f'{{!ltr model=linear_model1 \
                    efi.q2="{f2}" \
                    efi.q3="{f3}" \
                    efi.q4="{f4}" \
                    efi.q5="{f5}"}}',
                "fl": "id,[features]",   
                "rows": 50,
            }
                        
            docs = query_solr(payload) 
                        
            for doc in docs:
                docid = int(doc["id"])            
                feat_string = doc["[features]"]
                qid = int(q["id"])
                model_data_file.write( "{:s}\n".format( format_letor(qid, feat_string, docid, FEATURE_LIST) ) )  ###
                
        model_data_file.close()
        
    print(f"MODEL 1: number of queries: train {len(train_q)}, validation {len(validate_q)}, test {len(test_q)}")
    
    
def create_model2_data(FEATURE_LIST, train_q, validate_q, test_q):
    """
    Create the payload in JSON format for Model 2 to be sent to Solr
    Formats the response in LETOR dataset format
    Paramaters:
        FEATURE_LIST: list of feature names
        train_q: list of queries for training
        validation_q: list of queries for validation
        test_q: list of queries for testing
    Calls:
        query_solr(payload)
        format_letor(qid, feat_string, docid, FEATURE_LIST)
    """
    
    qid = 1
    for i, queries in enumerate([train_q, validate_q, test_q]):   
    
        model_data_file = open(FEATURE_FILE_TEMPLATE_MODEL2.format(FEAT_SUFFIXES[i]), "w")

        for q in queries:
            f1 = q["ss"]
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
            f_topic = str(q["qb_topic_id"])
            
            payload = {
                "q": f1,
                "defType": "edismax",
                "qf": "ss",
                "rq": f'{{!ltr model=linear_model2 \
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
                    efi.q28="{f28}" \
                    efi.q_topic="{f_topic}"}}',
                "fl": "score,id,[features]",   
                "rows": 50
            }
            
            docs = query_solr(payload) 
            
            for doc in docs:
                docid = int(doc["id"])            
                feat_string = doc["[features]"]
                qid = int(q["id"])
                model_data_file.write( "{:s}\n".format( format_letor(qid, feat_string, docid, FEATURE_LIST) ) )  
            
        model_data_file.close()

    print(f"MODEL 2: number of queries: train {len(train_q)}, validation {len(validate_q)}, test {len(test_q)}")
    
    
# COMPUTE and PREPEND RELEVANCE LABELS IN DATASETS

def get_data(data_type, model):
    """
    Parameters:
        data_type: one of the following strings:
            train, validate, test
        model: one of the following integers:
            1: for Model 1
            2: for Model 2
    Return: 
        FILE_READ: file path of file to be read
        FILE_WRITE: file path to write to
    """
    if model==1:
        if data_type == 'train':
            FILE_READ = FILE_MODEL1_NO_RELEVANCE_TRAIN
            FILE_WRITE = FILE_MODEL1_TRAIN
        
        elif data_type == 'validate':   
            FILE_READ = FILE_MODEL1_NO_RELEVANCE_VALIDATE
            FILE_WRITE = FILE_MODEL1_VALIDATE
        
        elif data_type == 'test':
            FILE_READ = FILE_MODEL1_NO_RELEVANCE_TEST
            FILE_WRITE = FILE_MODEL1_TEST

    elif model==2:
        if data_type == 'train':
            FILE_READ = FILE_MODEL2_NO_RELEVANCE_TRAIN
            FILE_WRITE = FILE_MODEL2_TRAIN
        
        elif data_type == 'validate':   
            FILE_READ = FILE_MODEL2_NO_RELEVANCE_VALIDATE
            FILE_WRITE = FILE_MODEL2_VALIDATE
        
        elif data_type == 'test':
            FILE_READ = FILE_MODEL2_NO_RELEVANCE_TEST
            FILE_WRITE = FILE_MODEL2_TEST

    return FILE_READ, FILE_WRITE


# The training, validation and test datasets created so far do not have the relevance label as the first item
# We prepend this relevance label here

def prepend_relevance_label_model1(FILE_READ, FILE_WRITE):
    """
    Prepend the relevance label to the dataset for Model 1
    Parameters:
        FILE_READ: file path for dataset to be read
        FILE_WRITE: file path to write to

    RELEVANCE = 1 if these feature values are >= 3.0:
    qa_pos           (feature 2)  
    qa_pos_bigram    (feature 3)     
    qa_pos_trigram   (feature 4)
    qa_parse_tree    (feature 5)    
    """
    data_list = []
    
    with open(FILE_READ, 'r') as fread:
        for line in fread:
            data_list.append(line)

    for i, record in enumerate(data_list):
        record_list = record.split()
        match=0
        score=0
        
        for k, feature in enumerate(record_list):
            if k==2 or k==3 or k==4 or k==5:
                pattern1 = fr'^{k}:0\.'
                pattern2 = fr'^{k}:1\.'
                pattern3 = fr'^{k}:2\.'
                
                match1 = re.match(pattern1,feature)
                match2 = re.match(pattern2,feature)
                match3 = re.match(pattern3,feature)
                
                if not match1 and not match2 and not match3:
                    match = 1
                else:
                    match = 0
                    
                score += match
                    
        if score==4:
            relevance = 1
        else:
            relevance = 0
        
        data_list[i] = str(relevance) + ' ' + record

    with open(FILE_WRITE, 'w') as fwrite:
        for x in data_list:
            fwrite.write(x)
            
            
def prepend_relevance_label_model2(FILE_READ, FILE_WRITE):
    """
    Prepend the relevance label to the dataset for Model 2
    Parameters:
        FILE_READ: file path for dataset to be read
        FILE_WRITE: file path to write to
    
    RELEVANCE = 1 if:
    ans_last_pos  (feature 25)  
    ans_length    (feature 28)     
    qb_topic_id   (feature 29)

    REVEVANCE = 2 if, additionally:
    ans_first_pos (feature 24)

    RELEVANCE = 3 if, additionally:
    ans_first     (feature 21)
    ans_last      (feature 22)
    """
    data_list = []
    
    with open(FILE_READ, 'r') as fread:
        for line in fread:
            data_list.append(line)

    for i, record in enumerate(data_list):
        record_list = record.split()
        match=0
        score1=0
        score2=0
        score3=0
        score4=0
        
        for k, feature in enumerate(record_list):
            if k==21 or k==22 or k==23 or k==24 or k==25 or k==28 or k==29:
                pattern = fr'^{k}:0'
                match = re.match(pattern,feature)
                
                if not match:
                    match = 1
                else:
                    match = 0
                
                if k==25 or k==28 or k==29:
                    score1 += match
                elif k==24:
                    score2 += match
                elif k==21 or k==22:    
                    score3 += match
                    
        if score3==2 and score2==1 and score1==3:
            relevance = 3
        elif score3!=2 and score2==1 and score1==3:
            relevance = 2
        elif score3!=2 and score2!=1 and score1==3:
            relevance = 1
        else:
            relevance = 0
        
        record = record.replace('29:0.0 ','')
        record = record.replace('29:1.0 ','')
        data_list[i] = str(relevance) + ' ' + record

    with open(FILE_WRITE, 'w') as fwrite:
        for x in data_list:
            fwrite.write(x)
            
            
def main():
    
    train_q, validate_q, test_q = create_query_lists()

    FEATURE_LIST_ONE = solr.feature_list(1)
    FEATURE_LIST_TWO = solr.feature_list(2)

    create_model1_data(FEATURE_LIST_ONE, train_q, validate_q, test_q)
    create_model2_data(FEATURE_LIST_TWO, train_q, validate_q, test_q)
    
    # MODEL 1
    FILE_READ, FILE_WRITE = get_data('train', 1)  
    prepend_relevance_label_model1(FILE_READ, FILE_WRITE)

    FILE_READ, FILE_WRITE = get_data('validate', 1)  
    prepend_relevance_label_model1(FILE_READ, FILE_WRITE)

    FILE_READ, FILE_WRITE = get_data('test', 1)  
    prepend_relevance_label_model1(FILE_READ, FILE_WRITE)

    # MODEL 2
    FILE_READ, FILE_WRITE = get_data('train', 2)  
    prepend_relevance_label_model2(FILE_READ, FILE_WRITE)

    FILE_READ, FILE_WRITE = get_data('validate', 2)  
    prepend_relevance_label_model2(FILE_READ, FILE_WRITE)

    FILE_READ, FILE_WRITE = get_data('test', 2)  
    prepend_relevance_label_model2(FILE_READ, FILE_WRITE)
    
    
if __name__ == '__main__':
    main()
