import pandas as pd
import matplotlib.pyplot as plt
# import numpy as np

# import scraped data
inputdata = pd.read_csv("web-scraping-data/referee_status_info.csv")


# Define simple methods that calculate the number of cards (all, yellow, red) per game that each referee has booked.
def get_cards_per_game(yellow: float, red: float, ngames: float) -> float:
    return round((yellow+red)/ngames,2)

def get_yellows_per_game(yellow: float, ngames: float) -> float:
    return round(yellow/ngames,2)

def get_reds_per_game(red: float, ngames: float) -> float:
    return round(red/ngames,2)

# Group data in order to combine the information for all available years that a referee has played.
groupdata = inputdata.groupby(by=["names", "from"], as_index=False).mean().round(2)

# Calculate the number of cards for each referee
groupdata["cards_per_game"] = [get_cards_per_game(x, y, z) for (x,y,z) in zip(groupdata["yellow"],groupdata["red"],groupdata["ngames"])]
groupdata["yellows_per_game"] = [get_yellows_per_game(x, z) for (x, z) in zip(groupdata["yellow"], groupdata["ngames"])]
groupdata["reds_per_game"] = [get_reds_per_game(y, z) for (y, z) in zip(groupdata["red"], groupdata["ngames"])]
groupdata = groupdata.drop(["yellow", "red"], axis=1)

# Define the basic referee's origins in order to filter them and plot each league independently
# Note: For England the column "from" has the interior names - 
#       So we consider each row not included on filterby names to describe english referees
filterby = ["Spain", "Germany", "France", "Switzerland", "Italy", "italy", "Russia"]

# Filter accordingly
spain = groupdata[groupdata["from"] == filterby[0]].reset_index(drop=True)
germany = groupdata[groupdata["from"] == filterby[1]].reset_index(drop=True)
france = groupdata[(groupdata["from"] == filterby[2]) | (groupdata["from"] == filterby[3])].reset_index(drop=True)
italy = groupdata[(groupdata["from"] == filterby[4]) | (groupdata["from"] == filterby[5])].reset_index(drop=True)
russia = groupdata[(groupdata["from"] == filterby[6])].reset_index(drop=True)
england = groupdata[~groupdata["from"].isin(filterby)].reset_index(drop=True)


# Remove outliers method
def remove_outliers(df: pd.DataFrame, hard_margin: int = 3) -> pd.DataFrame:

    print(f"Mean: {round(df['ngames'].mean(), 2)} + Std: {round(df['ngames'].std(), 2)}")
    low_margin = df["ngames"].mean() - 2*df["ngames"].std()
    low_margin = low_margin if low_margin > hard_margin else hard_margin 
    print(f"Low Margin {low_margin}")
    
    filter = (df["ngames"] >= low_margin) 
    return df.loc[filter]


# Remove outliers for each league
RemOut_spain = remove_outliers(spain)
RemOut_germany = remove_outliers(germany)
RemOut_france = remove_outliers(france)
RemOut_italy = remove_outliers(italy)
RemOut_russia = remove_outliers(russia)
RemOut_england = remove_outliers(england)

# Change column from to follow a unified pattern
RemOut_spain["from"] = ["Spain" for x in RemOut_spain["from"]]
RemOut_germany["from"] = ["Germany" for x in RemOut_germany["from"]]
RemOut_france["from"] = ["France" for x in RemOut_france["from"]]
RemOut_italy["from"] = ["Italy" for x in RemOut_italy["from"]]
RemOut_russia["from"] = ["Russia" for x in RemOut_russia["from"]]
RemOut_england["from"] = ["England" for x in RemOut_england["from"]]


# Print the number of removed outliers for each league
print(f"Initial number of rows for Spanish league was {len(spain)}. After removing outliers: {len(RemOut_spain)}")
print(f"Initial number of rows for German league was {len(germany)}. After removing outliers: {len(RemOut_germany)}")
print(f"Initial number of rows for French league was {len(france)}. After removing outliers: {len(RemOut_france)}")
print(f"Initial number of rows for Italian league was {len(italy)}. After removing outliers: {len(RemOut_italy)}")
print(f"Initial number of rows for Russian league was {len(russia)}. After removing outliers: {len(RemOut_russia)}")
print(f"Initial number of rows for English league was {len(england)}. After removing outliers: {len(RemOut_england)}")


# Instantiate the Dictionary to store results
data = dict()

def find_splitpoints(series: pd.Series) -> tuple:
    sortedSeries = series.sort_values().reset_index(drop=True)
    length = len(sortedSeries)
    splitpoint = int(length/3)
    return (sortedSeries[splitpoint],  sortedSeries[splitpoint*2])


# After removing low values we compute the basic statistics for each league
# Spain
margins = find_splitpoints(RemOut_spain["yellows_per_game"])
data["spain"] = margins

# Germany
margins = find_splitpoints(RemOut_germany["yellows_per_game"])
data["germany"] = margins

# France
margins = find_splitpoints(RemOut_france["yellows_per_game"])
data["france"] = margins

# Italy
margins = find_splitpoints(RemOut_italy["yellows_per_game"])
data["italy"] = margins

# Russia
margins = find_splitpoints(RemOut_russia["yellows_per_game"])
data["russia"] = margins

# England
margins = find_splitpoints(RemOut_england["yellows_per_game"])
data["england"] = margins


def assign_class(cards_per_game: float, league_name: str) -> str:
    low_margin, high_margin = data[league_name]
    if cards_per_game <= low_margin:
        return "Low"
    elif cards_per_game <= high_margin:
        return "Medium"
    else:
        return "High"

RemOut_spain["Class"] = [assign_class(x, "spain") for x in RemOut_spain["yellows_per_game"]]
RemOut_germany["Class"] = [assign_class(x, "germany") for x in RemOut_germany["yellows_per_game"]]
RemOut_france["Class"] = [assign_class(x, "france") for x in RemOut_france["yellows_per_game"]]
RemOut_italy["Class"] = [assign_class(x, "italy") for x in RemOut_italy["yellows_per_game"]]
RemOut_russia["Class"] = [assign_class(x, "russia") for x in RemOut_russia["yellows_per_game"]]
RemOut_england["Class"] = [assign_class(x, "england") for x in RemOut_england["yellows_per_game"]]


final_data = pd.concat([RemOut_spain, RemOut_germany, RemOut_france, RemOut_italy, RemOut_russia, RemOut_england])
final_data.to_csv("analysis/ref_category.csv", encoding='utf-8', index=False)
# sta onomata diaithtwn pou kophkan vale class inexp



















# Plot for each country
spain.plot.scatter(x="cards_per_game", y="ngames")
plt.show()

boxplot = spain.boxplot(column=["cards_per_game"], grid=False)
boxplot = russia.boxplot(column=["ngames"], grid=False)
