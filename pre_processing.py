import pandas as pd

"""
This script performs several data preprocessing steps to ensure data integrity.
Checking datatypes, dealing with missing values etc.
"""

path = "datasets/merged_datasets/"
data = pd.read_csv(path+"SpanishLaLiga14_15.csv")

print(data.dtypes)
print(data['Date'].dtypes)
print(data['Round'].dtypes)
























































