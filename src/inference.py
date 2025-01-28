import argparse

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--model_file", required=True, help="Parameter 1")
    parser.add_argument("--test_data", required=True, help="Parameter 2")
    parser.add_argument("--metrics_output", required=True, help="Parameter 2")
    
    args = parser.parse_args()
    
    print(args)
    
    print("inference_task!")