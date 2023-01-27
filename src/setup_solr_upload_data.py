# SETUP OF SOLR - UPLOADING DATA (1002 DOCUMENTS)

import os        # os.path.join
import csv       # csv.DictReader
import json      # json.dumps
import requests  # requests.post


DATA_DIR   = "data/"

FEATURE_DOC   = os.path.join(DATA_DIR, "feature/feature_doc.csv")
FEATURE_QUERY   = os.path.join(DATA_DIR, "feature/feature_query.csv")

SOLR_URL = "http://localhost:8983/solr/core1"

# UPLOAD DATA (i.e., DOCUMENT FEATURES) FROM CSV FILE TO SOLR

def add_record_to_solr(solr_url, 
                       id, 
                       qb_question,
                       qb_answer,
                       qb_choice1,
                       qb_choice2,
                       qb_choice3,
                       qb_topic_id,
                       topic,
                       qa, 
                       qa_pos,
                       qa_pos_bigram,
                       qa_pos_trigram,
                       qa_parse_tree,
                       ss, 
                       ss_pos,
                       ss_pos_bigram,
                       ss_pos_trigram,
                       ss_parse_tree,
                       before,
                       before_last,
                       before_last_pos,
                       before_pos,
                       before_pos_bigram,
                       before_pos_trigram,
                       before_parse_tree,
                       after,
                       after_first,
                       after_first_pos,
                       after_pos,
                       after_pos_bigram,
                       after_pos_trigram,
                       after_parse_tree,    
                       ans,
                       ans_first,
                       ans_last,
                       ans_pos,
                       ans_first_pos,
                       ans_last_pos,
                       ans_is_first, 
                       ans_is_last, 
                       ans_length,  
                       should_commit=False):
    """
    Parameters: values for fields in FEATURE_DOC
    
    The data is converted to JSON format and moved to Solr using Solr's HTTP API.
    The POST request is equivalent to this command in terminal:
    curl -X POST -H 'content-type:application/json' 'http://localhost:8983/solr/my_core/update' --data-binary  '[{...}]'   
    """
    
    headers = {
        "content-type": "application/json",
        "accept": "application/json"
    }
    
    if id is None:
        requests.post(solr_url + "update", params={"commit": "true"}, headers=headers)
    else:
        req_body = json.dumps({
            "add": {
                "doc": {
                    "id": id,        # name must be id in JSON (not doc_id)
                    "qb_question": qb_question,
                    "qb_answer": qb_answer,
                    "qb_choice1": qb_choice1,
                    "qb_choice2": qb_choice2,
                    "qb_choice3": qb_choice3,
                    "qb_topic_id": qb_topic_id,
                    "topic": topic,
                    "qa": qa,
                    "qa_pos": qa_pos,
                    "qa_pos_bigram": qa_pos_bigram,
                    "qa_pos_trigram": qa_pos_trigram,
                    "qa_parse_tree": qa_parse_tree,
                    "ss": ss,
                    "ss_pos": ss_pos,
                    "ss_pos_bigram": ss_pos_bigram,
                    "ss_pos_trigram": ss_pos_trigram,
                    "ss_parse_tree": ss_parse_tree,
                    "before": before,
                    "before_last": before_last,
                    "before_last_pos": before_last_pos,
                    "before_pos": before_pos,
                    "before_pos_bigram": before_pos_bigram,
                    "before_pos_trigram": before_pos_trigram,
                    "before_parse_tree": before_parse_tree,
                    "after": after,
                    "after_first": after_first,
                    "after_first_pos": after_first_pos,
                    "after_pos": after_pos,
                    "after_pos_bigram": after_pos_bigram,
                    "after_pos_trigram": after_pos_trigram,
                    "after_parse_tree": after_parse_tree,    
                    "ans": ans,
                    "ans_first": ans_first,
                    "ans_last": ans_last,
                    "ans_pos": ans_pos,
                    "ans_first_pos": ans_first_pos,
                    "ans_last_pos": ans_last_pos,
                    "ans_is_first": ans_is_first,
                    "ans_is_last": ans_is_last,
                    "ans_length":  ans_length
                }
            }
        })
        params = { "commit": "true" if should_commit else "false" }
        requests.post(solr_url + "/update", data=req_body, params=params, headers=headers)
        
        
def get_record_from_csv(filepath):
    """
    Parameter: 
        filepath: path of csv file of document data
    Calls: add_record_to_solr()
    """
    i = 0
    should_commit = False

    with open(filepath, "r") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            if i % 100 == 0:
                print(f"{i} records moved to Solr")
            
            id = int(row["id"])
            qb_question = row["qb_question"]
            qb_answer = row["qb_answer"]
            qb_choice1 = row["qb_choice1"]
            qb_choice2 = row["qb_choice2"]
            qb_choice3 = row["qb_choice3"]
            qb_topic_id = int(row["qb_topic_id"])
            topic = row["topic"]
            qa = row["qa"]
            qa_pos = row["qa_pos"]
            qa_pos_bigram = row["qa_pos_bigram"]
            qa_pos_trigram = row["qa_pos_trigram"]
            qa_parse_tree = row["qa_parse_tree"]
            ss = row["ss"]
            ss_pos = row["ss_pos"]
            ss_pos_bigram = row["ss_pos_bigram"]
            ss_pos_trigram = row["ss_pos_trigram"]
            ss_parse_tree = row["ss_parse_tree"]
            before = row["before"]
            before_last = row["before_last"]
            before_last_pos = row["before_last_pos"]
            before_pos = row["before_pos"]
            before_pos_bigram = row["before_pos_bigram"]
            before_pos_trigram = row["before_pos_trigram"]
            before_parse_tree = row["before_parse_tree"]
            after = row["after"]
            after_first = row["after_first"]
            after_first_pos = row["after_first_pos"]
            after_pos = row["after_pos"]
            after_pos_bigram = row["after_pos_bigram"]
            after_pos_trigram = row["after_pos_trigram"]
            after_parse_tree = row["after_parse_tree"]
            ans = row["ans"]
            ans_first = row["ans_first"]
            ans_last = row["ans_last"]
            ans_pos = row["ans_pos"]
            ans_first_pos = row["ans_first_pos"]
            ans_last_pos = row["ans_last_pos"]
            ans_is_first = row["ans_is_first"]
            ans_is_last = row["ans_is_last"]
            ans_length = row["ans_length"]
            
            add_record_to_solr(SOLR_URL, 
                               id, 
                               qb_question,
                               qb_answer,
                               qb_choice1,
                               qb_choice2,
                               qb_choice3,
                               qb_topic_id,
                               topic,
                               qa, 
                               qa_pos,
                               qa_pos_bigram,
                               qa_pos_trigram,
                               qa_parse_tree,
                               ss, 
                               ss_pos,
                               ss_pos_bigram,
                               ss_pos_trigram,
                               ss_parse_tree,
                               before,
                               before_last,
                               before_last_pos,
                               before_pos,
                               before_pos_bigram,
                               before_pos_trigram,
                               before_parse_tree,
                               after,
                               after_first,
                               after_first_pos,
                               after_pos,
                               after_pos_bigram,
                               after_pos_trigram,
                               after_parse_tree,    
                               ans,
                               ans_first,
                               ans_last,
                               ans_pos,
                               ans_first_pos,
                               ans_last_pos,
                               ans_is_first, 
                               ans_is_last, 
                               ans_length,  
                               should_commit=True)
            should_commit = False
            i += 1
            
    print(f"Total of {i} records moved to Solr")
    
    
def main():
    get_record_from_csv(FEATURE_DOC)
    get_record_from_csv(FEATURE_QUERY)
    
    
if __name__ == '__main__':
    main()