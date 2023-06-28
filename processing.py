import matplotlib.pyplot as plt
import pandas as pd

"""
This class performs the necessary processing steps to ensure data integrity.
It also performs feature enginnering 
"""


class process():
    
    def __init__(self, pair: tuple,
                       yellowLimit: int = 5,
                       redLimit: int = 0.25):
        
        self.data_details = pd.read_csv(pair[0])
        self.data_statistics = pd.read_csv(pair[1], encoding="latin-1")
        self.YellowLimit = yellowLimit
        self.RedLimit = redLimit
        print(f"The shape of loaded details data: {self.data_details.shape}")
        print(f"The shape of loaded statistics data: {self.data_statistics.shape}")
    
    def run(self):
        self.dataPreprocess()
        self.featureTransformation()
        self.dataPostprocess()
        return self.data
    
    
    def correct_date_format(self, date):
        split_date = date.split("/")
        if len(split_date[-1]) == 2:
            return date
        else:
            split_date[-1] = split_date[-1][-2:]
            return "/".join(split_date)
    
    
    def dataPreprocess(self):
        
        """
        Performs the following steps:
            1. Ensures date type integrity between two datasets
            2. Removes the % symbol from ball possession columns and turns the values into integers
            1. Merges the two datasets into one by joining on the common columns
            2. Transforms the Round column into integer (needed for sorting later)
            3. Creates three extra columns by adding the Yellow - Red - Second Yellow cards for both teams
        """
        self.data_details["Date"] = [self.correct_date_format(x) for x in self.data_details["Date"]]
        self.data_statistics["Date"] = [self.correct_date_format(x) for x in self.data_statistics["Date"]]
        
        self.data_statistics["HomeBallpossession"] = [int(x.replace("%", "")) for x in self.data_statistics["HomeBallpossession"]]
        self.data_statistics["AwayBallpossession"] = [int(x.replace("%", "")) for x in self.data_statistics["AwayBallpossession"]]
        
        self.data_details["Date"] = pd.to_datetime(self.data_details["Date"], format="%d/%m/%y")
        self.data_statistics["Date"] = pd.to_datetime(self.data_statistics["Date"], format="%d/%m/%y")
        
        
        self.data = self.data_details.merge(self.data_statistics, on=["Date", "Round", "HomeTeam", "AwayTeam"])
        
        
        self.data["Round"] = [int(x.replace("Round ", "")) for x in self.data["Round"]]
        self.data["Yellows"] = self.data["HomeYellows"] + self.data["AwayYellows"]
        self.data["Reds"] = self.data["HomeReds"] + self.data["AwayReds"]
        self.data["secondYellows"] = self.data["HomeSecondYellows"] + self.data["AwaySecondYellows"]
        

    
    def plot(self):
        
        """
        Visualization of basic Yellow cards by round statistics
        """
        
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
        
    def eda_analysis(self):
        return
    
    def featureTransformation(self):
        
        """
        Input: positions (list of integers) that denote key positions in the
               leaderboard that could potentially describe team's goal.
               The default values are 4/7/18 denoting the corresponding positions
               that lead either on champions league, or europa league or relegation.
               This is an open variable to the user since different leagues
               have different key positions.
        
        Performs the following steps:
            1. Based on the given values of list *'positions'* creates the equivalent
               features that denote for each match the distance of each team from these positions
            2. It creates two new features based the sum of the yellow cards each team had
               on the past 3 matches
        """
        
        new_order = list(range(len(self.data)-1, -1, -1))
        self.data = self.data.iloc[new_order]
        self.data.reset_index(inplace=True, drop=True)
        
        # positions = positions if positions else [4, 7, 18]
        # positions_dict = {}
        # feature_text = "diff_from_pos"
        # for position in positions:
        #     if position > 20:
        #         continue
            
        #     positions_dict["pos" + str(position)] = position
        #     for status in ["home", "away"]:
        #         self.data[feature_text + str(position) + status] = 0
            
        self.data["difference"] = 0
        
        teams = set(self.data['HomeTeam'])
        team_points = {team: 0 for team in teams}
        
        # Initialize the new feature columns with zeros
        self.data["past_three_yellow_cards_home"], self.data["past_three_yellow_cards_away"] = 0, 0
        yellow_cards_count = {team:[] for team in teams}
        
        self.data["past_three_tackles_home"], self.data["past_three_tackles_away"] = 0, 0
        tackles_count = {team:[] for team in teams}
        
        self.data["past_three_ball_possession_home"], self.data["past_three_ball_possession_away"] = 0, 0
        ball_possession_count = {team:[] for team in teams}
        
        self.data["past_three_possession_lost_home"], self.data["past_three_possession_lost_away"] = 0, 0
        possession_lost_count = {team:[] for team in teams}
        
        self.data["past_three_interceptions_home"], self.data["past_three_interceptions_away"] = 0, 0
        interceptions_count = {team:[] for team in teams}
        
        self.data["past_three_fouls_home"], self.data["past_three_fouls_away"] = 0, 0
        fouls_count = {team:[] for team in teams}
        
        self.data["past_three_duels_won_home"], self.data["past_three_duels_won_away"] = 0, 0
        duels_won_count = {team:[] for team in teams}
        
        self.data["past_three_aerials_won_home"], self.data["past_three_aerials_won_away"] = 0, 0
        aerials_won_count = {team:[] for team in teams}
        
        #TODO: Keep from here to compute the past three
        
        for _, group in self.data.groupby("Round"):
            
            # sorted_teams = sorted(team_points.items(), key=lambda x: x[1], reverse=True)

            # points = {}
            # for key, value in positions_dict.items():
            #     points[key] = sorted_teams[value-1][1]


            for index, row in group.iterrows():
                
                # For the current match isolate the following features (both home and away):
                # Teams
                home_team, away_team = row['HomeTeam'], row['AwayTeam']
                # Goals
                home_goals, away_goals = row['HomeGoals'], row['AwayGoals']
                # Yellow cards
                home_yellows, away_yellows = row["HomeYellows"], row["AwayYellows"]
                # Tackles
                home_tackles, away_tackles = row["HomeTackles"], row["AwayTackles"]
                # Ball possession
                home_ballpossession, away_ballpossession = row["HomeBallpossession"], row["AwayBallpossession"]
                # Possessions lost
                home_possessionlost, away_possessionlost = row["HomePossessionlost"], row["AwayPossessionlost"]
                # Interceptions
                home_interceptions, away_interceptions = row["HomeInterceptions"], row["AwayInterceptions"]
                # Fouls
                home_fouls, away_fouls = row["HomeFouls"], row["AwayFouls"]
                # Duels won
                home_duelswon, away_duelswon = row["HomeDuelswon"], row["AwayDuelswon"]
                # Aerials won
                home_aerialswon, away_aerialswon = row["HomeAerialswon"], row["AwayAerialswon"]
                
                
                
                self.data.loc[index, "difference"] = abs(team_points[home_team] - team_points[away_team])
                # for key, value in positions_dict.items():
                #     self.data.loc[index, feature_text + str(value) + "home"] = team_points[home_team] - points[str(key)]
                #     self.data.loc[index, feature_text + str(value) + "away"] = team_points[away_team] - points[str(key)]
                        
        
                # Assign the yellow cards count for the home and away teams as new columns in the dataframe
                self.data.at[index, 'past_three_yellow_cards_home'] = sum(yellow_cards_count[home_team][-3:])
                self.data.at[index, 'past_three_yellow_cards_away'] = sum(yellow_cards_count[away_team][-3:])
                
                # Assign the yellow cards count for the home and away teams as new columns in the dataframe
                self.data.at[index, 'past_three_tackles_home'] = sum(tackles_count[home_team][-3:])
                self.data.at[index, 'past_three_tackles_away'] = sum(tackles_count[away_team][-3:])
                
                # Assign the yellow cards count for the home and away teams as new columns in the dataframe
                self.data.at[index, 'past_three_ball_possession_home'] = sum(ball_possession_count[home_team][-3:])
                self.data.at[index, 'past_three_ball_possession_away'] = sum(ball_possession_count[away_team][-3:])
                
                # Assign the yellow cards count for the home and away teams as new columns in the dataframe
                self.data.at[index, 'past_three_possession_lost_home'] = sum(possession_lost_count[home_team][-3:])
                self.data.at[index, 'past_three_possession_lost_away'] = sum(possession_lost_count[away_team][-3:])
                
                # Assign the yellow cards count for the home and away teams as new columns in the dataframe
                self.data.at[index, 'past_three_interceptions_home'] = sum(interceptions_count[home_team][-3:])
                self.data.at[index, 'past_three_interceptions_away'] = sum(interceptions_count[away_team][-3:])
                
                # Assign the yellow cards count for the home and away teams as new columns in the dataframe
                self.data.at[index, 'past_three_fouls_home'] = sum(fouls_count[home_team][-3:])
                self.data.at[index, 'past_three_fouls_away'] = sum(fouls_count[away_team][-3:])
                
                # Assign the yellow cards count for the home and away teams as new columns in the dataframe
                self.data.at[index, 'past_three_duels_won_home'] = sum(duels_won_count[home_team][-3:])
                self.data.at[index, 'past_three_duels_won_away'] = sum(duels_won_count[away_team][-3:])
                
                # Assign the yellow cards count for the home and away teams as new columns in the dataframe
                self.data.at[index, 'past_three_aerials_won_home'] = sum(aerials_won_count[home_team][-3:])
                self.data.at[index, 'past_three_aerials_won_away'] = sum(aerials_won_count[away_team][-3:])
                
                
                # Update yellow cards count for home and away teams
                yellow_cards_count[home_team].append(home_yellows)
                yellow_cards_count[away_team].append(away_yellows)
                
                tackles_count[home_team].append(home_tackles)
                tackles_count[away_team].append(away_tackles)
                
                ball_possession_count[home_team].append(home_ballpossession)
                ball_possession_count[away_team].append(away_ballpossession)
                
                possession_lost_count[home_team].append(home_possessionlost)
                possession_lost_count[away_team].append(away_possessionlost)
                
                interceptions_count[home_team].append(home_interceptions)
                interceptions_count[away_team].append(away_interceptions)
                
                fouls_count[home_team].append(home_fouls)
                fouls_count[away_team].append(away_fouls)
                
                duels_won_count[home_team].append(home_duelswon)
                duels_won_count[away_team].append(away_duelswon)
                
                aerials_won_count[home_team].append(home_aerialswon)
                aerials_won_count[away_team].append(away_aerialswon)
                
                # Update team points based on match result
                if home_goals > away_goals:
                    team_points[home_team] += 3
                elif home_goals < away_goals:
                    team_points[away_team] += 3
                else:
                    team_points[home_team] += 1
                    team_points[away_team] += 1
        
    
    def dataPostprocess(self):
        
        # self.data = self.data[self.data["Round"] > 5]
        self.data = self.data.drop(["Date", "Location", "Stadium", 
                                    "HomeYellows", "HomeReds", "HomeSecondYellows", 
                                    "AwayYellows", "AwayReds", "AwaySecondYellows",
                                    "HomeTeam", "HomeGoals", "AwayTeam", "AwayGoals"], axis=1)
        

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
        


