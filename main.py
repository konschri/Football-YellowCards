from src.processing import process
from src.basicml import MLPipeline
from src.dim_reduction import Analyzer
from typing import List, Tuple
import pandas as pd
import glob


def main(csv_files: List[Tuple[str, str]],
         reduction: str = None, 
         algorithm: str ="xgb"):
    
    """
    The options for the inputs are:
        analysis -> "factor", "pca"
        algorithm -> "rf", "lr", "xgb"
    """
    
    # Iterate over each CSV file and process it according to processing module
    dataframes = []
    for pair in csv_files:
        seasonInstance = process(pair)
        dataframes.append(seasonInstance.run())
    
    print("Data have been processed.")
    
    # Let the last pair of data as test set
    train_df = pd.concat(dataframes[:-1], ignore_index=True)
    test_df = dataframes[-1]
    
    # Use the respective reduction method
    if reduction == "factor":
        train_df, test_df = Analyzer.factoranalysis(train_df, test_df)
    elif reduction == "pca":
        train_df, test_df = Analyzer.principalcomponentsanalysis(train_df, test_df)
    else:
        print("You didn't select a proper reduction option") 
        print("Options are: 'factor' or 'pca'")
        pass
    
    # Use the respective algorithm
    if algorithm in ["rf", "lr", "xgb"]:
        pr = MLPipeline(train_df, test_df, algorithm=algorithm)
        pr.run()
    else:
        raise ValueError("You didn't select a proper algorithm option")
    
    return


if __name__ == "__main__":
    
    folder_path_details = "datasets\\datasets_details\\"
    folder_path_statistics = "datasets\\datasets_statistics\\"
    csv_files_details = glob.glob(folder_path_details + "*.csv")
    csv_files_statistics = glob.glob(folder_path_statistics + "*.csv")
    assert len(csv_files_details) == len(csv_files_statistics)
    csv_files = list(zip(csv_files_details, csv_files_statistics))
    
    #TODO: Consider using argparse for the inputs
    reduction = "factor"
    algorithm = "xgb"
    
    main(csv_files, reduction, algorithm)
