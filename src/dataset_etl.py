import argparse

from src.query.dataset_etl import *

from config.logging_config import get_logger
logger = get_logger()


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--output_file", required=True, help="Parameter 1")
    
    args = parser.parse_args()
    
    logger.info(args)

    train_dataset_query = generate_train_dataset_query()

    logger.info(train_dataset_query)