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
for pair in csv_files[3:]:
 
    # Process the data according to process class
    seasonInstance = process(pair)
    
    # Append the resulted dataframe to the list
    dataframes.append(seasonInstance.run())



combined_df = pd.concat(dataframes, ignore_index=True)
combined_df = combined_df.drop(["Reds", "RedRefCategory"], axis=1)
outliersfree = combined_df[combined_df["Yellows"] <10]
combined_df["Yellows"].plot(kind='kde')
combined_df["Yellows"].plot(kind='hist', edgecolor='black')
combined_df["Yellows"].value_counts().sort_index()
outliersfree["Yellows"].value_counts().sort_index()
df2=combined_df.corr()


pr = MLPipeline(combined_df)
pr.run()


# combined_df.to_csv("ref_data.csv", encoding='utf-8', index=False)




#%%
#from sofascore_scrapper import SofaScoreScraper
from sofascore_scrapper_match_stats import SofaScoreScraperMatchStats

url = "https://www.sofascore.com/tournament/football/spain/laliga/8"
league_name = "Spanish La Liga"
Y = 1150
season_code = "1"

scrpr = SofaScoreScraperMatchStats(url, league_name, season_code)
scrpr.scrape()


#%%

import pandas as pd
from processing import process
from BasicML import MLPipeline


a, b = csv_files[3][0], csv_files[3][1]
instance = process((a, b))
prpr = instance.dataPreprocess()
norpr = instance.featureTransformation(prpr)
final = instance.dataPostprocess(norpr)

pr = MLPipeline(final)
pr.run()

data_details = pd.read_csv(a)
data_statistics = pd.read_csv(b, encoding="latin-1")

def correct_date_format(date):
    split_date = date.split("/")
    if len(split_date[-1]) == 2:
        return date
    else:
        split_date[-1] = split_date[-1][-2:]
        return "/".join(split_date)


data_details["Date"] = [correct_date_format(x) for x in data_details["Date"]]
data_statistics["Date"] = [correct_date_format(x) for x in data_statistics["Date"]]


data_details["Date"] = pd.to_datetime(data_details["Date"], format="%d/%m/%y")
data_statistics["Date"] = pd.to_datetime(data_statistics["Date"], format="%d/%m/%y")


data = data_details.merge(data_statistics, on=["Date", "Round", "HomeTeam", "AwayTeam"])






































