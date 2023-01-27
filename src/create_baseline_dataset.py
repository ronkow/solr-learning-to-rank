# CREATING DATASETS for BASELINE MODELS
# To create baseline datasets, simply edit the model datasets to include only the first feature value: BM25 on sentence (Model 1) or substring (Model 2).

import os 

DATA_DIR   = "data/model/"

FILE_MODEL1_TRAIN    = os.path.join(DATA_DIR, "model1_train.txt")
FILE_MODEL1_VALIDATE = os.path.join(DATA_DIR, "model1_validate.txt")
FILE_MODEL1_TEST     = os.path.join(DATA_DIR, "model1_test.txt")

FILE_MODEL2_TRAIN    = os.path.join(DATA_DIR, "model2_train.txt")
FILE_MODEL2_VALIDATE = os.path.join(DATA_DIR, "model2_validate.txt")
FILE_MODEL2_TEST     = os.path.join(DATA_DIR, "model2_test.txt")


FILE_MODEL1_TRAIN_BASELINE    = os.path.join(DATA_DIR, "baseline_model1_train.txt")
FILE_MODEL1_VALIDATE_BASELINE = os.path.join(DATA_DIR, "baseline_model1_validate.txt")
FILE_MODEL1_TEST_BASELINE     = os.path.join(DATA_DIR, "baseline_model1_test.txt")

FILE_MODEL2_TRAIN_BASELINE    = os.path.join(DATA_DIR, "baseline_model2_train.txt")
FILE_MODEL2_VALIDATE_BASELINE = os.path.join(DATA_DIR, "baseline_model2_validate.txt")
FILE_MODEL2_TEST_BASELINE     = os.path.join(DATA_DIR, "baseline_model2_test.txt")


def get_final_data(data_type, model):
    """
    Parameters:
        data_type: One of the following strings:
            train, validate, test
        model: One of the following integers:
            1: Model 1
            2: Model 2
    Return:
        FILE_READ: path of file to be read
        FILE_WRITE: path of file to write to
    """
    if model==1:
        if data_type == 'train':
            FILE_READ = FILE_MODEL1_TRAIN
            FILE_WRITE = FILE_MODEL1_TRAIN_BASELINE
        
        elif data_type == 'validate':   
            FILE_READ = FILE_MODEL1_VALIDATE
            FILE_WRITE = FILE_MODEL1_VALIDATE_BASELINE
        
        elif data_type == 'test':
            FILE_READ = FILE_MODEL1_TEST
            FILE_WRITE = FILE_MODEL1_TEST_BASELINE

    elif model==2:
        if data_type == 'train':
            FILE_READ = FILE_MODEL2_TRAIN
            FILE_WRITE = FILE_MODEL2_TRAIN_BASELINE
        
        elif data_type == 'validate':   
            FILE_READ = FILE_MODEL2_VALIDATE
            FILE_WRITE = FILE_MODEL2_VALIDATE_BASELINE
        
        elif data_type == 'test':
            FILE_READ = FILE_MODEL2_TEST
            FILE_WRITE = FILE_MODEL2_TEST_BASELINE

    return FILE_READ, FILE_WRITE   

            
def baseline_dataset(FILE_READ, FILE_WRITE, model):
    """
    Creates the dataset for the baseline model by selecting the required features (and values) from the dataset with all features
    Parameters:
        FILE_READ: Path of file to be read
        FILE_WRITE: Path of file to write to
        model: One of the following strings:
           train, validate, test
    """
    data_list = []
    baseline_data_list = []
    
    with open(FILE_READ, 'r') as fread:
        for line in fread:
            data_list.append(line)

    for i, record in enumerate(data_list):
        record_list = record.split()
        
        for k, feature in enumerate(record_list):
            if model==1:
                if k==0:
                    baseline_data_list.append(feature)
                elif k==1 or k==2 or k==7:
                    baseline_data_list[i] += ' ' + feature
                elif k==8:
                    baseline_data_list[i] += ' ' + feature + '\n'
            
            elif model==2:
                if k==0:
                    baseline_data_list.append(feature)   
                elif k==1 or k==2 or k==30:
                    baseline_data_list[i] += ' ' + feature
                elif k==31:
                    baseline_data_list[i] += ' ' + feature + '\n' 

    with open(FILE_WRITE, 'w') as fwrite:
        for x in baseline_data_list:
            fwrite.write(x)
            
            
def main():
    # MODEL 1
    FILE_READ, FILE_WRITE = get_final_data('train', 1)  
    baseline_dataset(FILE_READ, FILE_WRITE, 1)

    FILE_READ, FILE_WRITE = get_final_data('validate', 1)  
    baseline_dataset(FILE_READ, FILE_WRITE, 1)

    FILE_READ, FILE_WRITE = get_final_data('test', 1)  
    baseline_dataset(FILE_READ, FILE_WRITE, 1)

    # MODEL 2
    FILE_READ, FILE_WRITE = get_final_data('train', 2)  
    baseline_dataset(FILE_READ, FILE_WRITE, 2)

    FILE_READ, FILE_WRITE = get_final_data('validate', 2)  
    baseline_dataset(FILE_READ, FILE_WRITE, 2)

    FILE_READ, FILE_WRITE = get_final_data('test', 2)  
    baseline_dataset(FILE_READ, FILE_WRITE, 2)
    
    
if __name__ == '__main__':
    main()
            
            
            
