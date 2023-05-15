# This script is only used to merge the data of each season in a unified csv per season.
# Adjust accordingly the results of scraping
import pandas as pd

path = "datasets/initial_datasets/"
league = "SpanishLaLiga"
season = "21_22"
rest = "_rest"
read_path = path + league + season

# Reading part. 
df1 = pd.read_csv(read_path + ".csv", encoding="latin-1")
df2 = pd.read_csv(read_path + rest + ".csv", encoding="latin-1")
#df3 = pd.read_csv("datasets/initial_datasets/SpanishLaLiga15_16_round0.csv", encoding="latin-1")


# Merging part. Adjust 
finalcsv = pd.concat([df1, df2], axis=0).reset_index(drop=True)

# Saving the seasonal csv
export = "datasets/merged_datasets/"
export_path = export + league + season 
finalcsv.to_csv(export_path + ".csv", encoding="utf-8", index=False)
