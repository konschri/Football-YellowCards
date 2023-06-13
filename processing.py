import matplotlib.pyplot as plt
from statistics import mean
import numpy as np
import pandas as pd
import time

"""
This class performs the necessary processing steps to ensure data integrity.
It also performs feature enginnering 
"""


class process():
    
    def __init__(self, filename, yellowLimit=5, redLimit=0.25):
        path = "datasets/merged_datasets/"
        self.filename = filename
        self.data = pd.read_csv(path+self.filename)
        self.YellowLimit = yellowLimit
        self.RedLimit = redLimit
        print(f"The shape of loaded data: {self.data.shape}")
    
    def dataPreprocess(self):
        
        self.data["Round"] = [int(x.replace("Round ", "")) for x in self.data["Round"]]
        self.data["Yellows"] = self.data["HomeYellows"] + self.data["AwayYellows"]
        self.data["Reds"] = self.data["HomeReds"] + self.data["AwayReds"]
        self.data["secondYellows"] = self.data["HomeSecondYellows"] + self.data["AwaySecondYellows"]
        
        
        
        #print(f"The average amount of Yellow cards per game is {round(self.data['Yellows'].mean(), 2)}")
        return self.data

    
    def plot(self):
        yellowsByRound = self.data.groupby(["Round"])["Yellows"].mean()
        yellowsByRound.sort_index(inplace=True)
        
        plt.figure(figsize=(10,6))
        plt.plot(yellowsByRound, marker="o")
        plt.axhline(yellowsByRound.mean(), color='red', linestyle='--')
        plt.xlabel("Round")
        plt.ylabel("Cards")
        plt.title("Average Yellow Cards per round")
        plt.xticks(yellowsByRound.index, rotation=45)
        plt.tight_layout()
        plt.show()
        
    
    def featureTransformation(self, *positions):
        """
        Input list of integers smaller than 20
        """
        new_order = list(range(len(self.data)-1, -1, -1))
        self.data = self.data.iloc[new_order]
        self.data.reset_index(inplace=True, drop=True)
        
        positions = positions if positions else [4, 7, 18]
        positions_dict = {}
        feature_text = "diff_from_pos"
        for position in positions:
            if position > 20:
                continue
            
            positions_dict["pos" + str(position)] = position
            for status in ["home", "away"]:
                self.data[feature_text + str(position) + status] = 0
            
        self.data["difference"] = 0
        
        
        
        # Initialize the new feature columns with zeros
        self.data['past_three_yellow_cards_home'] = 0
        self.data['past_three_yellow_cards_away'] = 0
        
        teams = set(self.data['HomeTeam'])
        team_points = {team: 0 for team in teams}
        
        yellow_cards_count = {team:[] for team in teams}
        
        
        
        for _, group in self.data.groupby("Round"):
            
            sorted_teams = sorted(team_points.items(), key=lambda x: x[1], reverse=True)

            points = {}
            for key, value in positions_dict.items():
                points[key] = sorted_teams[value-1][1]


            for index, row in group.iterrows():
                
                # Teams of current match
                home_team, away_team = row['HomeTeam'], row['AwayTeam']
                
                # Score of current match
                home_goals, away_goals = row['HomeGoals'], row['AwayGoals']
                
                # Yellow cards of current match
                home_yellows, away_yellows = row["HomeYellows"], row["AwayYellows"]
                
                self.data.loc[index, "difference"] = abs(team_points[home_team] - team_points[away_team])
                for key, value in positions_dict.items():
                    self.data.loc[index, feature_text + str(value) + "home"] = team_points[home_team] - points[str(key)]
                    self.data.loc[index, feature_text + str(value) + "away"] = team_points[away_team] - points[str(key)]
                        
        
                # Assign the yellow cards count for the home and away teams as new columns in the dataframe
                self.data.at[index, 'past_three_yellow_cards_home'] = sum(yellow_cards_count[home_team][-3:])
                self.data.at[index, 'past_three_yellow_cards_away'] = sum(yellow_cards_count[away_team][-3:])
                
                
                # Update yellow cards count for home and away teams
                yellow_cards_count[home_team].append(home_yellows)
                yellow_cards_count[away_team].append(away_yellows)
                
                
                # Update team points based on match result
                if home_goals > away_goals:
                    team_points[home_team] += 3
                elif home_goals < away_goals:
                    team_points[away_team] += 3
                else:
                    team_points[home_team] += 1
                    team_points[away_team] += 1
        
        self.data = self.data.drop(["Date", "Location", "Stadium", 
                                    "HomeYellows", "HomeReds", "HomeSecondYellows", 
                                    "AwayYellows", "AwayReds", "AwaySecondYellows"], axis=1)
        
        return self.data
    
    def dataPostprocess(self):
        self.data = self.data[self.data["Round"] > 5]
        print(self.data.head())
        self.data.drop(["HomeTeam", "HomeGoals", "AwayTeam", "AwayGoals", "Round"], axis=1, inplace=True)   
        # self.data.drop(["HomeYellows", "HomeReds", "HomeSecondYellows", "AwayYellows", "AwayReds", "AwaySecondYellows"], axis=1, inplace=True)

        # The splitting points for each Referee is 5 yellow cards and 0.25 red cards by default
        self.data["YellowRefCategory"] = [1 if x > self.YellowLimit else 0 for x in self.data["RefereeYellows"]]
        self.data["RedRefCategory"] = [1 if x > self.RedLimit else 0 for x in self.data["RefereeReds"]]
        self.data.drop(['Referee', 'RefereeYellows', 'RefereeReds'], axis=1, inplace=True)
        
        
        self.data.fillna(self.data.mean().astype(int), inplace=True)
        
        
        self.data["Yellows"] = [x + y for x,y in zip(self.data["Yellows"], self.data["secondYellows"])]
        self.data["Reds"] = [x + y for x,y in zip(self.data["Reds"], self.data["secondYellows"])]
        
        self.data.drop(["secondYellows"], axis=1, inplace=True)
        

        # final_data = data.copy()
        return self.data.copy()
        


