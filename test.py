"""
test for calling objects
"""

from processing import process
from BasicML import MLPipeline
import pandas as pd
import glob

folder_path = "datasets/merged_datasets/"
csv_files = glob.glob(folder_path + "*.csv")

dataframes = []

# Iterate over each CSV file
for file in csv_files:
    # Read the CSV file as a dataframe
    df = pd.read_csv(file)
    # Append the dataframe to the list
    dataframes.append(df)




a = process("SpanishLaLiga17_18.csv")
data1 = a.dataPreprocess()
data2 = a.featureTransformation(1, 4, 7, 18)
data3 = a.dataPostprocess()
    
pr = MLPipeline(data3)
pr.run()
