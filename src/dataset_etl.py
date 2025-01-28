import argparse

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--output_file", required=True, help="Parameter 1")
    
    args = parser.parse_args()
    
    print(args)
    
    print("dataset_etl_task!")