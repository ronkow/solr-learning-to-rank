# SETUP OF SOLR - UPLOADING OF MODEL 1 and MODEL 2

import os        
import json      
import requests
import solr

MODEL_DIR  = "model/"

SOLR_MODEL1 = os.path.join(MODEL_DIR, "model1.json")
SOLR_MODEL2 = os.path.join(MODEL_DIR, "model2.json")

SOLR_URL = "http://localhost:8983/solr/core1" 

headers = {"Content-type": "application/json"}


def upload_model_to_solr(SOLR_MODEL, SOLR_URL):
    """
    Upload model to model store in Solr
    Parameters:
        SOLR_MODEL: path of tree model file in JSON format
        SOLR_URL: path of model store in Solr
    """
    lines = []

    with open(SOLR_MODEL, "r") as fjson:
        for line in fjson:
            lines.append(line.strip())
        
    data = " ".join(lines)
    resp = requests.put(SOLR_URL + "/schema/model-store", headers=headers, data=data)
    print(resp.text)
    
    
def main():
    # Delete all existing MS first

    solr.delete_model_store(SOLR_URL + "/schema/model-store/linear_model1")
    solr.delete_model_store(SOLR_URL + "/schema/model-store/linear_model2")

    solr.delete_model_store(SOLR_URL + "/schema/model-store/lambdamart_model1")
    solr.delete_model_store(SOLR_URL + "/schema/model-store/lambdamart_model2")

    solr.delete_model_store(SOLR_URL + "/schema/model-store/lambdamart_model1_baseline")
    solr.delete_model_store(SOLR_URL + "/schema/model-store/lambdamart_model2_baseline")

    upload_model_to_solr(SOLR_MODEL1, SOLR_URL)
    upload_model_to_solr(SOLR_MODEL2, SOLR_URL)


if __name__ == '__main__':
    main()