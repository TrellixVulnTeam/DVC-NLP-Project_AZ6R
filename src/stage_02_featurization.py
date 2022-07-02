import argparse
import os
import numpy as np
import shutil
from tqdm import tqdm
import logging
from src.utils.common import read_yaml, create_directories, get_df
from src.utils.data_mgmt import process_posts
import random
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer

STAGE = "Featurization" ## <<< change stage name 

logging.basicConfig(
    filename=os.path.join("logs", 'running_logs.log'), 
    level=logging.INFO, 
    format="[%(asctime)s: %(levelname)s: %(module)s]: %(message)s",
    filemode="a"
    )

def main(config_path, params_path):
    ## read config files
    config = read_yaml(config_path)
    params = read_yaml(params_path)

    artifacts = config["artifacts"]
    prepare_data_dir_path = os.path.join(artifacts["ARTIFACTS_DIR"], artifacts["PREPARED_DATA"])
    train_data_path  = os.path.join(prepare_data_dir_path,artifacts["TRAIN_DATA"])      # features will be saved at this path
    test_data_path = os.path.join(prepare_data_dir_path,artifacts["TEST_DATA"])

    featurized_data_dir_path=  os.path.join(artifacts['ARTIFACTS_DIR'], artifacts["FEATURIZED_DATA"])
    create_directories([featurized_data_dir_path])
    
    featurized_train_data_path=  os.path.join(featurized_data_dir_path, artifacts["FEATURIZED_DATA_TRAIN"])      
    featurized_test_data_path=  os.path.join(featurized_data_dir_path, artifacts["FEATURIZED_DATA_TEST"])
           
    max_features = params['featurize']['max_features']      # features 
    n_grams = params['featurize']['n_grams']

    df_train = get_df(train_data_path)
    train_words = np.array(df_train.text.str.lower().values.astype("U")) # will convert into unique

    bag_of_words= CountVectorizer(
        stop_words= "english",
        max_features =  max_features, 
        ngram_range = (1, n_grams)
    )

    bag_of_words.fit(train_words)
    train_words_binary_matrix = bag_of_words.transform(train_words)

    tfid= TfidfTransformer(smooth_idf= False)
    tfid.fit(train_words_binary_matrix)
    train_words_tfidf_matrix = tfid.transform(train_words_binary_matrix)

    # for test data 
    df_test = get_df(test_data_path)
    test_words = np.array(df_test.text.str.lower().values.astype("U")) # will convert into unique
    test_words_binary_matrix = bag_of_words.transform(test_words)
    test_words_tfidf_matrix = tfid.transform(test_words_binary_matrix)
    # call a function to save this matrix
    

if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument("--config", "-c", default="configs/config.yaml")
    args.add_argument("--params", "-p", default="params.yaml")
    parsed_args = args.parse_args()

    try:
        logging.info("\n********************")
        logging.info(f">>>>> stage {STAGE} started <<<<<")
        main(config_path=parsed_args.config, params_path=parsed_args.params)
        logging.info(f">>>>> stage {STAGE} completed!<<<<<\n")
    except Exception as e:
        logging.exception(e)
        raise e