# UPLOADING OF LINEAR MODEL DEFINITIONS TO SOLR for FEATURE VALUE EXTRACTION

import json 
import solr

SOLR_URL = "http://localhost:8983/solr/core1"

headers = {"Content-type": "application/json"}


def main():
    # Delete all existing MS first
    solr.delete_model_store(SOLR_URL + "/schema/model-store/linear_model1")
    solr.delete_model_store(SOLR_URL + "/schema/model-store/linear_model2")

    solr.delete_model_store(SOLR_URL + "/schema/model-store/lambdamart_model1")
    solr.delete_model_store(SOLR_URL + "/schema/model-store/lambdamart_model2")

    solr.delete_model_store(SOLR_URL + "/schema/model-store/lambdamart_model1_baseline")
    solr.delete_model_store(SOLR_URL + "/schema/model-store/lambdamart_model2_baseline")


    ms1 = solr.model_store1()
    ms2 = solr.model_store2()

    solr.create_model_store(SOLR_URL + "/schema/model-store", headers, json.dumps(ms1))
    solr.create_model_store(SOLR_URL + "/schema/model-store", headers, json.dumps(ms2))
    
if __name__ == '__main__':
    main()