import requests

# To amend features, delete old features and old model-store first

def delete_feature_store(path):
    """
    Delete an existing feature store in the file _schema_feature-store.json in Solr
    Print the response
    Parameter: 
        path: path of the feature store, e.g. http://localhost:8983/solr/core1/schema/feature-store/feature_store1
    """
    resp = requests.delete(path)
    print(resp.text)
    
def delete_model_store(path):
    """
    Delete an existing model store file in the file _schema_model-store.json Solr
    Print the response
    Parameter: 
        path: path of the model store
            e.g. http://localhost:8983/solr/core1/schema/model-store/linear_model1
    """
    resp = requests.delete(path)
    print(resp.text)

    
# Create feature store and model store

def create_feature_store(path, headers, data):
    """
    Create a new feature store
    Print the response
    Parameters:
       path: path of the feature store
           e.g. http://localhost:8983/solr/core1/schema/feature-store
       headers: header in JSON format 
           {"Content-type": "application/json"}
       data: data in JSON format 
           json.dumps(...)
    """
    resp = requests.put(path, headers=headers, data=data)
    print(resp.text)
    
def create_model_store(path, headers, data):
    """
    Create a new model store
    Print the response
    Parameters:
       path: path of the model store
           e.g. http://localhost:8983/solr/core1/schema/model-store
       headers: header in JSON format 
           {"Content-type": "application/json"}
       data: data in JSON format
           json.dumps(...)
    """    
    resp = requests.put(path, headers=headers, data=data)
    print(resp.text)
    

def feature_store1():
    """
    Definition of feature store 1 in JSON format
    """
    fs1 = [
        {
            # qa1  
            "store": "feature_store1",
            "name": "qa_original_score",
            "class": "org.apache.solr.ltr.feature.OriginalScoreFeature",
            "params": {}
        },
        {
            # qa2  
            "store": "feature_store1",
            "name": "qa_pos",
            "class": "org.apache.solr.ltr.feature.SolrFeature", 
            "params": { "q": "{!dismax qf=qa_pos}${q2}" }
        },
        {
            # qa3 
            "store": "feature_store1",
            "name": "qa_pos_bigram",
            "class": "org.apache.solr.ltr.feature.SolrFeature", 
            "params": { "q": "{!dismax qf=qa_pos_bigram}${q3}" }
        },
        {
            #  qa4 
            "store": "feature_store1",
            "name": "qa_pos_trigram",
            "class": "org.apache.solr.ltr.feature.SolrFeature",   
            "params": { "q": "{!dismax qf=qa_pos_trigram}${q4}" }     
        },
        {
            #   qa5
            "store": "feature_store1",
            "name": "qa_parse_tree",
            "class": "org.apache.solr.ltr.feature.SolrFeature",   
            "params": { "q": "{!dismax qf=qa_parse_tree}${q5}" }     
        },
    ]
    return fs1


def model_store1():
    """
    Definition of model store for linear_model1 in JSON format
    """
    ms1 = {
        "store" : "feature_store1",
        "name" : "linear_model1",
        "class" : "org.apache.solr.ltr.model.LinearModel",
        "features" : [
            { "name": "qa_original_score" },
            { "name": "qa_pos" },  
            { "name": "qa_pos_bigram" },
            { "name": "qa_pos_trigram" },
            { "name": "qa_parse_tree" },
        ],
        "params" : {
            "weights" : {
                "qa_original_score": 1.0,
                "qa_pos": 0.0,
                "qa_pos_bigram": 0.0,
                "qa_pos_trigram": 0.0,
                "qa_parse_tree": 0.0,
            }
        }
    }
    return ms1


def feature_store2():
    """
    Definition of feature store 2 in JSON format
    """
    fs2 = [
        {
            # ss1  
            "store": "feature_store2",
            "name": "ss_original_score",
            "class": "org.apache.solr.ltr.feature.OriginalScoreFeature",
            "params": {}
        },
        {
            # ss2  
            "store": "feature_store2",
            "name": "ss_pos",
            "class": "org.apache.solr.ltr.feature.SolrFeature", 
            "params": { "q": "{!dismax qf=ss_pos}${q2}" }
        },
        {
            # ss3 
            "store": "feature_store2",
            "name": "ss_pos_bigram",
            "class": "org.apache.solr.ltr.feature.SolrFeature", 
            "params": { "q": "{!dismax qf=ss_pos_bigram}${q3}" }
        },
        {
            #  ss4 
            "store": "feature_store2",
            "name": "ss_pos_trigram",
            "class": "org.apache.solr.ltr.feature.SolrFeature",   
            "params": { "q": "{!dismax qf=ss_pos_trigram}${q4}" }     
        },
        {
            #   ss5
            "store": "feature_store2",
            "name": "ss_parse_tree",
            "class": "org.apache.solr.ltr.feature.SolrFeature",   
            "params": { "q": "{!dismax qf=ss_parse_tree}${q5}" }     
        },
        {
            #  b1   
            "store": "feature_store2",
            "name": "before",
            "class": "org.apache.solr.ltr.feature.SolrFeature",   
            "params": { "q": "{!dismax qf=before}${q6}" }     
        },
        {
            #   b2
            "store": "feature_store2",
            "name": "before_last",
            "class": "org.apache.solr.ltr.feature.SolrFeature",   
            "params": { "fq": ["{!term f=before_last}${q7}"] }   #       
        },
        {
            #  b3 
            "store": "feature_store2",
            "name": "before_last_pos",
            "class": "org.apache.solr.ltr.feature.SolrFeature",   
            "params": { "fq": ["{!term f=before_last_pos}${q8}"] }  #
        },
        {
            #  b4 
            "store": "feature_store2",
            "name": "before_pos",
            "class": "org.apache.solr.ltr.feature.SolrFeature",   
            "params": { "q": "{!dismax qf=before_pos}${q9}" }     
        },
        {
            #   b5
            "store": "feature_store2",
            "name": "before_pos_bigram",
            "class": "org.apache.solr.ltr.feature.SolrFeature",   
            "params": { "q": "{!dismax qf=before_pos_bigram}${q10}" }     
        },
        {
            #   b6
            "store": "feature_store2",
            "name": "before_pos_trigram",
            "class": "org.apache.solr.ltr.feature.SolrFeature",   
            "params": { "q": "{!dismax qf=before_pos_trigram}${q11}" }     
        },
        {
            #   b7
            "store": "feature_store2",
            "name": "before_parse_tree",
            "class": "org.apache.solr.ltr.feature.SolrFeature",   
            "params": { "q": "{!dismax qf=before_parse_tree}${q12}" }     
        },
        {
            #  a1   
            "store": "feature_store2",
            "name": "after",
            "class": "org.apache.solr.ltr.feature.SolrFeature",   
            "params": { "q": "{!dismax qf=after}${q13}" }     
        },
        {
            #   a2
            "store": "feature_store2",
            "name": "after_first",
            "class": "org.apache.solr.ltr.feature.SolrFeature",   
            "params": { "fq": ["{!term f=after_first}${q14}"] }  #      
        },
        {
            #  a3 
            "store": "feature_store2",
            "name": "after_first_pos",
            "class": "org.apache.solr.ltr.feature.SolrFeature",   
            "params": { "fq": ["{!term f=after_first_pos}${q15}"] }  # 
        },
        {
            #  a4 
            "store": "feature_store2",
            "name": "after_pos",
            "class": "org.apache.solr.ltr.feature.SolrFeature",   
            "params": { "q": "{!dismax qf=after_pos}${q16}" }     
        },
        {
            #   a5
            "store": "feature_store2",
            "name": "after_pos_bigram",
            "class": "org.apache.solr.ltr.feature.SolrFeature",   
            "params": { "q": "{!dismax qf=after_pos_bigram}${q17}" }     
        },
        {
            #   a6
            "store": "feature_store2",
            "name": "after_pos_trigram",
            "class": "org.apache.solr.ltr.feature.SolrFeature",   
            "params": { "q": "{!dismax qf=after_pos_trigram}${q18}" }     
        },
        {
            #   a7
            "store": "feature_store2",
            "name": "after_parse_tree",
            "class": "org.apache.solr.ltr.feature.SolrFeature",   
            "params": { "q": "{!dismax qf=after_parse_tree}${q19}" }     
        },
        {
            #   ans1
            "store": "feature_store2",
            "name": "ans",
            "class": "org.apache.solr.ltr.feature.SolrFeature",   
            "params": { "q": "{!dismax qf=ans}${q20}" }     
        },
        {
            # ans2   
            "store": "feature_store2",
            "name": "ans_first",
            "class": "org.apache.solr.ltr.feature.SolrFeature", 
            "params": { "fq": ["{!term f=ans_first}${q21}"] }  # 
        },
        {
            #   ans3
            "store": "feature_store2",
            "name": "ans_last",
            "class": "org.apache.solr.ltr.feature.SolrFeature", 
            "params": { "fq": ["{!term f=ans_last}${q22}"] }  # 
        },
        {
            #   ans4   
            "store": "feature_store2",    
            "name": "ans_pos",    
            "class": "org.apache.solr.ltr.feature.SolrFeature",    
            "params": { "fq": ["{!term f=ans_pos}${q23}"] }  # 
        },
        {
            #   ans5    
            "store": "feature_store2",    
            "name": "ans_first_pos",    
            "class": "org.apache.solr.ltr.feature.SolrFeature",    
            "params": { "fq": ["{!term f=ans_first_pos}${q24}"] }  #
        },
        {
            #   ans6    
            "store": "feature_store2",    
            "name": "ans_last_pos",    
            "class": "org.apache.solr.ltr.feature.SolrFeature",    
            "params": { "fq": ["{!term f=ans_last_pos}${q25}"] }  # 
        },
        {
            #   ans7    
            "store": "feature_store2",    
            "name": "ans_is_first",    
            "class": "org.apache.solr.ltr.feature.SolrFeature",    
            "params": { "fq": ["{!term f=ans_is_first}${q26}"] }  # 
        },
        {
            #   ans8    
            "store": "feature_store2",    
            "name": "ans_is_last",    
            "class": "org.apache.solr.ltr.feature.SolrFeature",    
            "params": { "fq": ["{!term f=ans_is_last}${q27}"] }  # 
        },
        {
            #   ans9    
            "store": "feature_store2",    
            "name": "ans_length",    
            "class": "org.apache.solr.ltr.feature.SolrFeature",    
            "params": { "fq": ["{!term f=ans_length}${q28}"] }  #
        },
        {
            #  topic_id included only for data prep. Remove this when uploading fs1 to Solr.  
            "store": "feature_store2",    
            "name": "qb_topic_id",    
            "class": "org.apache.solr.ltr.feature.SolrFeature",    
            "params": { "fq": ["{!term f=qb_topic_id}${q_topic}"] }  #
        },
    ]
    return fs2


def model_store2():
    """
    Definition of model store for linear_model2 in JSON format, including the feature qb_topic_id
    """
    ms2 = {
        "store" : "feature_store2",
        "name" : "linear_model2",
        "class" : "org.apache.solr.ltr.model.LinearModel",
        "features" : [
            { "name": "ss_original_score" },
            { "name": "ss_pos" },  
            { "name": "ss_pos_bigram" },
            { "name": "ss_pos_trigram" },
            { "name": "ss_parse_tree" },
            
            { "name": "before" },  
            { "name": "before_last" },  
            { "name": "before_last_pos" },
            { "name": "before_pos" },  
            { "name": "before_pos_bigram" },  
            { "name": "before_pos_trigram" },
            { "name": "before_parse_tree" },  
            
            { "name": "after" },  
            { "name": "after_first" },  
            { "name": "after_first_pos" },
            { "name": "after_pos" },  
            { "name": "after_pos_bigram" },  
            { "name": "after_pos_trigram" },
            { "name": "after_parse_tree" },  
            { "name": "ans" },
    
            { "name": "ans_first" },
            { "name": "ans_last" },
            { "name": "ans_pos" },
            { "name": "ans_first_pos" },
            { "name": "ans_last_pos" },         
            { "name": "ans_is_first" },   
            { "name": "ans_is_last" }, 
            { "name": "ans_length" },
            { "name": "qb_topic_id" },  
        ],
        "params" : {
            "weights" : {
                "ss_original_score": 1.0,
                "ss_pos": 0.0,
                "ss_pos_bigram": 0.0,
                "ss_pos_trigram": 0.0,
                "ss_parse_tree": 0.0,
                "before": 0.0,
                "before_last": 0.0,
                "before_last_pos": 0.0,
                "before_pos": 0.0,
                "before_pos_bigram": 0.0,
                "before_pos_trigram": 0.0,
                "before_parse_tree": 0.0,
                "after": 0.0,
                "after_first": 0.0,
                "after_first_pos": 0.0,
                "after_pos": 0.0,
                "after_pos_bigram": 0.0,
                "after_pos_trigram": 0.0,
                "after_parse_tree": 0.0,
                "ans": 0.0,
                "ans_first": 0.0,
                "ans_last": 0.0,
                "ans_pos": 0.0,
                "ans_first_pos": 0.0,
                "ans_last_pos": 0.0,
                "ans_is_first": 0.0,
                "ans_is_last": 0.0,
                "ans_length": 0.0,
                "qb_topic_id": 0.0,  
            }
        }
    }
    return ms2


# model store with no qb_topic_id

def model_store2_final():
    """
    Definition of model store for linear_model2 in JSON format, excluding the feature qb_topic_id
    """
    ms2 = {
        "store" : "feature_store2",
        "name" : "linear_model2",
        "class" : "org.apache.solr.ltr.model.LinearModel",
        "features" : [
            { "name": "ss_original_score" },
            { "name": "ss_pos" },  
            { "name": "ss_pos_bigram" },
            { "name": "ss_pos_trigram" },
            { "name": "ss_parse_tree" },
            
            { "name": "before" },  
            { "name": "before_last" },  
            { "name": "before_last_pos" },
            { "name": "before_pos" },  
            { "name": "before_pos_bigram" },  
            { "name": "before_pos_trigram" },
            { "name": "before_parse_tree" },  
            
            { "name": "after" },  
            { "name": "after_first" },  
            { "name": "after_first_pos" },
            { "name": "after_pos" },  
            { "name": "after_pos_bigram" },  
            { "name": "after_pos_trigram" },
            { "name": "after_parse_tree" },  
            { "name": "ans" },
    
            { "name": "ans_first" },
            { "name": "ans_last" },
            { "name": "ans_pos" },
            { "name": "ans_first_pos" },
            { "name": "ans_last_pos" },         
            { "name": "ans_is_first" },   
            { "name": "ans_is_last" }, 
            { "name": "ans_length" },
        ],
        "params" : {
            "weights" : {
                "ss_original_score": 1.0,
                "ss_pos": 0.0,
                "ss_pos_bigram": 0.0,
                "ss_pos_trigram": 0.0,
                "ss_parse_tree": 0.0,
                "before": 0.0,
                "before_last": 0.0,
                "before_last_pos": 0.0,
                "before_pos": 0.0,
                "before_pos_bigram": 0.0,
                "before_pos_trigram": 0.0,
                "before_parse_tree": 0.0,
                "after": 0.0,
                "after_first": 0.0,
                "after_first_pos": 0.0,
                "after_pos": 0.0,
                "after_pos_bigram": 0.0,
                "after_pos_trigram": 0.0,
                "after_parse_tree": 0.0,
                "ans": 0.0,
                "ans_first": 0.0,
                "ans_last": 0.0,
                "ans_pos": 0.0,
                "ans_first_pos": 0.0,
                "ans_last_pos": 0.0,
                "ans_is_first": 0.0,
                "ans_is_last": 0.0,
                "ans_length": 0.0,
            }
        }
    }
    return ms2


def feature_list(model):
    """
    Lists of feature names for Model 1 and Model 2
    """
    FEATURE_LIST_ONE = [
        "qa_original_score",
        "qa_pos",
        "qa_pos_bigram",
        "qa_pos_trigram",
        "qa_parse_tree"
    ]
    
    FEATURE_LIST_TWO = [
        "ss_original_score",
        "ss_pos",
        "ss_pos_bigram",
        "ss_pos_trigram",    
        "ss_parse_tree",    
        "before",    
        "before_last",    
        "before_last_pos",    
        "before_pos",    
        "before_pos_bigram",    
        "before_pos_trigram",
        "before_parse_tree",
        "after",    
        "after_first",    
        "after_first_pos",    
        "after_pos",    
        "after_pos_bigram",    
        "after_pos_trigram",    
        "after_parse_tree",    
        "ans",    
        "ans_first",    
        "ans_last",
        "ans_pos",    
        "ans_first_pos",    
        "ans_last_pos",    
        "ans_is_first",    
        "ans_is_last",    
        "ans_length",    
        "qb_topic_id",   # Only for data prep. Remove qb_topic_id for training.
    ]    
    
    FEATURE_LIST_ONE_BASELINE = ["qa_original_score"]
    
    FEATURE_LIST_TWO_BASELINE = ["ss_original_score"]
  

    if model==1:
        return FEATURE_LIST_ONE
    elif model==2:
        return FEATURE_LIST_TWO
    elif model==3:
        return FEATURE_LIST_ONE_BASELINE
    elif model==4:
        return FEATURE_LIST_TWO_BASELINE