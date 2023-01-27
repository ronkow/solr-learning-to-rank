'''
MODEL BUILDING

Use the LambdaMART algorithm in the LTR library RankLib:
https://sourceforge.net/p/lemur/wiki/RankLib/

Download RankLib-2.15.jar from:
https://sourceforge.net/projects/lemur/files/lemur/RankLib-2.15/

To train, validate and test a model, run the following command:
- java -jar RankLib-2.15.jar -train ../path/train.txt -test ../path/test.txt -validate ../path/validate.txt -ranker 6 -metric2t NDCG@10 -metric2T NDCG@10 -save ../path/model.txt

- ranker 6 refers to LambdaMART.
- metric2t refers to the metric to optimize on the training data.
- metric2T refers to the metric to evaluate on the test data. If not specified, it will use the same metric as metric2t.
- Supported metrics are: MAP, NDCG@k, DCG@k, P@k, RR@k, ERR@k. The default metric is ERR@10.

'''

# CONVERTING MODELS TO JSON FORMAT
# LambdaMART outputs the model in txt format. We need to convert the model to JSON format before uploading it to Solr.

import os        
import json      
import xml.etree.ElementTree as ET   # ET.parse
import solr


MODEL_DIR  = "model/"

MODEL1_TXT = os.path.join(MODEL_DIR, "model1.txt")
MODEL1_XML = os.path.join(MODEL_DIR, "model1.xml")
MODEL1_JSON = os.path.join(MODEL_DIR, "model1.json")

MODEL2_TXT = os.path.join(MODEL_DIR, "model2.txt")
MODEL2_XML = os.path.join(MODEL_DIR, "model2.xml")
MODEL2_JSON = os.path.join(MODEL_DIR, "model2.json")

BASELINE_MODEL1_TXT = os.path.join(MODEL_DIR, "baseline_model1.txt")
BASELINE_MODEL1_XML = os.path.join(MODEL_DIR, "baseline_model1.xml")
BASELINE_MODEL1_JSON = os.path.join(MODEL_DIR, "baseline_model1.json")

BASELINE_MODEL2_TXT = os.path.join(MODEL_DIR, "baseline_model2.txt")
BASELINE_MODEL2_XML = os.path.join(MODEL_DIR, "baseline_model2.xml")
BASELINE_MODEL2_JSON = os.path.join(MODEL_DIR, "baseline_model2.json")


def txt_to_xml(FILE_TXT, FILE_XML):
    """
    Convert the tree model (txt format) to xml format
    Parameters:
        FILE_TXT: path of text file to be read
        FILE_XML: path of xml file to write to
    """
    ftxt = open(FILE_TXT, "r")
    fxml = open(FILE_XML, "w")
    
    fxml.write("<?xml version=\"1.0\"?>\n")
    
    for line in ftxt:
        if line.startswith("##") or len(line.strip()) == 0:
            continue
        fxml.write("{:s}".format(line))
    fxml.close()
    ftxt.close()
    
    
def parse_split(el_split, feature_id2name, split_type="root"):
    """
    Parameters:
        el_split
        feature_id2name: id and name of feature 
        split_type: "root"
    Return: Tree node definition in JSON format
    """
    if split_type != "root":
        split_type = el_split.attrib["pos"]
        
    output = el_split.find("output")
    
    if output is not None:
        return {
            "value": output.text.strip()
        }
    
    feature = feature_id2name[int(el_split.find("feature").text.strip())]
    threshold = el_split.find("threshold").text.strip()
    el_csplits = el_split.findall("split")
    
    for el_csplit in el_csplits:
        attr_pos = el_csplit.attrib["pos"]
        
        if attr_pos == "left":
            left = parse_split(el_csplit, feature_id2name, "left")
        elif attr_pos == "right":
            right = parse_split(el_csplit, feature_id2name, "right")
            
    return {
        "feature": feature,
        "threshold": threshold,
        "left": left,
        "right": right
    }


def xml_to_json(FILE_XML, FILE_JSON, FEATURE_LIST, feature_store, model_name):
    """
    Convert the tree model (xml format) to JSON format
    Parameters:
        FILE_XML: tree model in XML format
        FILE_JSON: tree model in JSON format
        FEATURE_LIST: list of feature names
        feature_store: name of feature store
        model_name: name of model store
    Calls:
        parse_split(el_split, feature_id2name)
    """
    trees = []
    feature_id2name = {i+1:f for i, f in enumerate(FEATURE_LIST)}
    xml = ET.parse(FILE_XML)
    el_ensemble = xml.getroot()
    
    for el_tree in el_ensemble:
        weight = el_tree.attrib["weight"]
        el_split = el_tree.find("split")
        tree_dict = {
            "weight": weight,
            "root": parse_split(el_split, feature_id2name)
        }
        trees.append(tree_dict)
    
    params_dict = {"trees" : trees}
    
    features = [{"name": f} for f in FEATURE_LIST]

    model_dict = {
        "store": feature_store,
        "name": model_name,
        "class": "org.apache.solr.ltr.model.MultipleAdditiveTreesModel",
        "features": features,
        "params": params_dict
    }

    with open(FILE_JSON, "w") as fjson:
        fjson.write(json.dumps(model_dict, indent=4))
        
        
def main():
    txt_to_xml(MODEL1_TXT, MODEL1_XML)
    txt_to_xml(MODEL2_TXT, MODEL2_XML)

    txt_to_xml(BASELINE_MODEL1_TXT, BASELINE_MODEL1_XML)
    txt_to_xml(BASELINE_MODEL2_TXT, BASELINE_MODEL2_XML)


    FEATURE_LIST_ONE = solr.feature_list(1)
    FL2 = solr.feature_list(2)

    FEATURE_LIST_TWO = FL2[:-1]   # remove topic_id


    FEATURE_LIST_ONE_BASELINE = solr.feature_list(3)
    FEATURE_LIST_TWO_BASELINE = solr.feature_list(4)


    xml_to_json(MODEL1_XML, MODEL1_JSON, FEATURE_LIST_ONE, 'feature_store1', 'lambdamart_model1')
    xml_to_json(MODEL2_XML, MODEL2_JSON, FEATURE_LIST_TWO, 'feature_store2', 'lambdamart_model2')

    xml_to_json(BASELINE_MODEL1_XML, BASELINE_MODEL1_JSON, FEATURE_LIST_ONE_BASELINE, 'feature_store1', 'lambdamart_model1_baseline')
    xml_to_json(BASELINE_MODEL2_XML, BASELINE_MODEL2_JSON, FEATURE_LIST_TWO_BASELINE, 'feature_store2', 'lambdamart_model2_baseline')


if __name__ == '__main__':
    main()