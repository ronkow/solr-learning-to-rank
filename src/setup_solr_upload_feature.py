# SETUP OF SOLR - UPLOADING OF FEATURES FOR MODEL 1 and MODEL 2

import json 
import solr

SOLR_URL = "http://localhost:8983/solr/core1"                       

headers = {"Content-type": "application/json"}


def main():
    # Delete old FS first
    solr.delete_feature_store(SOLR_URL + "/schema/feature-store/feature_store1")
    solr.delete_feature_store(SOLR_URL + "/schema/feature-store/feature_store2")

    fs1 = solr.feature_store1()
    fs2 = solr.feature_store2()

    fs1 = solr.feature_store1()

    fs2_original = solr.feature_store2()
    fs2 = fs2_original[:-1]               # remove topic_id, which is required only for creating model datasets

    solr.create_feature_store(SOLR_URL + "/schema/feature-store", headers, json.dumps(fs1))
    solr.create_feature_store(SOLR_URL + "/schema/feature-store", headers, json.dumps(fs2))
    
    
if __name__ == '__main__':
    main()