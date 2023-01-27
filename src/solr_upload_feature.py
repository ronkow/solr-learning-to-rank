# UPLOADING OF FEATURE DEFINITIONS TO SOLR for FEATURE VALUE EXTRACTION

import json 
import solr

SOLR_URL = "http://localhost:8983/solr/core1"

headers = {"Content-type": "application/json"}

def main():
    # Delete all existing FS first
    solr.delete_feature_store(SOLR_URL + "/schema/feature-store/feature_store1")
    solr.delete_feature_store(SOLR_URL + "/schema/feature-store/feature_store2")

    fs1 = solr.feature_store1()
    fs2 = solr.feature_store2()

    solr.create_feature_store(SOLR_URL + "/schema/feature-store", headers, json.dumps(fs1))
    solr.create_feature_store(SOLR_URL + "/schema/feature-store", headers, json.dumps(fs2))
    
    
if __name__ == '__main__':
    main()