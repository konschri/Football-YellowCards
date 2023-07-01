"""
test for calling objects
"""
from processing import process
from BasicML import MLPipeline
import pandas as pd
import glob

folder_path_details = "datasets\\datasets_details\\"
folder_path_statistics = "datasets\\datasets_statistics\\"


csv_files_details = glob.glob(folder_path_details + "*.csv")
csv_files_statistics = glob.glob(folder_path_statistics + "*.csv")


assert len(csv_files_details) == len(csv_files_statistics)
csv_files = list(zip(csv_files_details, csv_files_statistics))

dataframes = []
# Iterate over each CSV file
for pair in csv_files[3:-1]:
 
    # Process the data according to process class
    seasonInstance = process(pair)  
    
    # Append the resulted dataframe to the list
    dataframes.append(seasonInstance.run())
    



train_df = pd.concat(dataframes[:-1], ignore_index=True)
test_df = dataframes[-1]

correlation_matrix = train_df.corr()
print(correlation_matrix)

pr = MLPipeline(train_df, test_df, algorithm="randomforest")
pr.run()


