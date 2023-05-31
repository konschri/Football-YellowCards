import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time

"""
This script performs several data preprocessing steps to ensure data integrity.
Checking datatypes, dealing with missing values etc.
"""


class process():
    
    def __init__(self, filename):
        path = "datasets/merged_datasets/"
        self.filename = filename
        self.data = pd.read_csv(path+self.filename)
        print(f"The shape of loaded data: {self.data.shape}")
    
    def dataPreprocess(self):
        
        self.data["Round"] = [int(x.replace("Round ", "")) for x in self.data["Round"]]
        self.data["Yellows"] = self.data["HomeYellows"] + self.data["AwayYellows"]
        self.data["Reds"] = self.data["HomeReds"] + self.data["AwayReds"]
        self.data["secondYellows"] = self.data["HomeSecondYellows"] + self.data["AwaySecondYellows"]
        
        
        self.data = self.data.drop(["Date", "Location", "Stadium", 
                                    "HomeYellows", "HomeReds", "HomeSecondYellows", 
                                    "AwayYellows", "AwayReds", "AwaySecondYellows"], axis=1)
        print(f"The average amount of Yellow cards per game is {round(self.data['Yellows'].mean(), 2)}")
        return self.data

        
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
        
        
        teams = set(self.data['HomeTeam'])
        team_points = {team: 0 for team in teams}
        
        
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
                               
                self.data.loc[index, "difference"] = abs(team_points[home_team] - team_points[away_team])
                for key, value in positions_dict.items():
                    self.data.loc[index, feature_text + str(value) + "home"] = team_points[home_team] - points[str(key)]
                    self.data.loc[index, feature_text + str(value) + "away"] = team_points[away_team] - points[str(key)]
                        

                # Update team points based on match result
                if home_goals > away_goals:
                    team_points[home_team] += 3
                elif home_goals < away_goals:
                    team_points[away_team] += 3
                else:
                    team_points[home_team] += 1
                    team_points[away_team] += 1
        return self.data
    
    def dataPostprocess(self):
        self.data = self.data[self.data["Round"] > 5]
        self.data.drop(["HomeTeam","HomeGoals", "AwayTeam", "AwayGoals", "Round"], axis=1, inplace=True)   
        self.data.drop(["HomeYellows", "HomeReds", "HomeSecondYellows", "AwayYellows", "AwayReds", "AwaySecondYellows"], axis=1, inplace=True)

        # The splitting points for each Referee is 5 yellow cards and 0.25 red cards
        YellowLimit, RedLimit = 5, 0.25
        self.data["YellowRefCategory"] = [1 if x > YellowLimit else 0 for x in self.data["RefereeYellows"]]
        self.data["RedRefCategory"] = [1 if x > RedLimit else 0 for x in self.data["RefereeReds"]]
        self.data.drop(['Referee', 'RefereeYellows', 'RefereeReds'], axis=1, inplace=True)
        
        
        self.data.fillna(self.data.mean().astype(int), inplace=True)
        
        
        self.data["Yellows"] = [x + y for x,y in zip(self.data["Yellows"], self.data["secondYellows"])]
        self.data["Reds"] = [x + y for x,y in zip(self.data["Reds"], self.data["secondYellows"])]
        
        self.data.drop(["secondYellows"], axis=1, inplace=True)
        

        # final_data = data.copy()
        return self.data.copy()
        


from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

class BasicMLPipeline():
    
    def __init__(self, data, reds=False):
        self.data = data
        self.reds = reds
        if self.reds:
            self.data.drop(["Yellows"], axis=1, inplace=True)
            self.Y = self.data["Reds"]
            self.X = self.data.drop(["Reds"], axis=1)
        else:
            self.data.drop(["Reds"], axis=1, inplace=True)
            self.Y = self.data["Yellows"]
            self.X = self.data.drop(["Yellows"], axis=1)
   
        
    def split(self):
        return train_test_split(self.X, self.Y, test_size=0.2, random_state=42)
    
    def scale(self):
        self.X_train, self.X_test, self.Y_train, self.Y_test = self.split(self.X, self.Y)
        scaler = StandardScaler()
        self.X_train = scaler.fit_transform(self.X_train)
        self.X_test = scaler.transform(self.X_test)
        
    def predict(self):
        clf = RandomForestRegressor(random_state=9)
        
        param_grid = {
                    "n_estimators" : [50, 100, 200, 300],
                    "max_depth" : [2, 3, 5]
                     }
        
        self.grid = GridSearchCV(estimator=clf, param_grid=param_grid, n_jobs=-1, verbose=2, cv=5)
        self.grid.fit(self.X_train, self.Y_train)
    
    def results(self):
        print(self.grid.best_estimator_)
        results = self.grid.predict(self.X_test)
        model_mse = mean_squared_error(self.Y_test, results)
        print(type(model_mse))
        
        baseline = np.repeat(5, len(results))
        baseline_mse = mean_squared_error(self.Y_test, baseline)
        print(type(baseline_mse))
        
        


"""
path = "datasets/merged_datasets/"
data = pd.read_csv(path+"SpanishLaLiga17_18.csv")
print(data.shape)

data = data.drop(["Date", "Location", "Stadium"], axis=1)
print(data.shape)

data["Round"] = [int(x.replace("Round ", "")) for x in data["Round"]]

# print(data.dtypes)
# print(data['Date'].dtypes)
# print(data['Round'].dtypes)




data["Yellows"] = data["HomeYellows"] + data["AwayYellows"]
data["Reds"] = data["HomeReds"] + data["AwayReds"]
data["secondYellows"] = data["HomeSecondYellows"] + data["AwaySecondYellows"]


print(round(data["Yellows"].mean(), 2))

yellowsByRound = data.groupby(["Round"])["Yellows"].mean()
yellowsByRound.sort_index(inplace=True)


# Plot
plt.figure(figsize=(10,6))
plt.plot(yellowsByRound, marker="o")
plt.axhline(yellowsByRound.mean(), color='red', linestyle='--')
# Set the names for axes and title
plt.xlabel("Round")
plt.ylabel("Cards")
plt.title("Average Yellow Cards per round")
plt.xticks(yellowsByRound.index, rotation=45)
plt.tight_layout()
plt.show()

#%%
new_order = list(range(len(data)-1, -1, -1))
data = data.iloc[new_order]
data.reset_index(inplace=True, drop=True)


teams = set(data['HomeTeam'])
team_points = {team: 0 for team in teams}

data['diff_from_pos4home'] = 0
data['diff_from_pos7home'] = 0
data['diff_from_pos18home'] = 0
data['diff_from_pos4away'] = 0
data['diff_from_pos7away'] = 0
data['diff_from_pos18away'] = 0
data["difference"] = 0

# data.groupby("Round")
for _, group in data.groupby("Round"):
    # time.sleep(1)
    # print(group)
    
    sorted_teams = sorted(team_points.items(), key=lambda x: x[1], reverse=True)
    pos4_points, pos7_points, pos18_points = sorted_teams[3][1], sorted_teams[6][1], sorted_teams[17][1]
    
    
    
    for index, row in group.iterrows():
        
        
        # Teams of current match
        home_team = row['HomeTeam']
        away_team = row['AwayTeam']
        # Points of each team
        homePoints = team_points[home_team]
        awayPoints = team_points[away_team]
        
        home_goals = row['HomeGoals']
        away_goals = row['AwayGoals']
        
        # print(f"{home_team} - {away_team}")
        # print(f"{home_goals} - {away_goals}")
        # print(f"{homePoints} - {awayPoints}")
        
        
        diff_from_opponent= abs(team_points[home_team] - team_points[away_team])
        diff_from_pos4home, diff_from_pos7home, diff_from_pos18home = team_points[home_team]-pos4_points, team_points[home_team]-pos7_points, team_points[home_team]-pos18_points
        diff_from_pos4away, diff_from_pos7away, diff_from_pos18away = team_points[away_team]-pos4_points, team_points[away_team]-pos7_points, team_points[away_team]-pos18_points
        data.loc[index, "diff_from_pos4home"] = diff_from_pos4home
        data.loc[index, "diff_from_pos7home"] = diff_from_pos7home
        data.loc[index, "diff_from_pos18home"] = diff_from_pos18home
        
        data.loc[index, "diff_from_pos4away"] = diff_from_pos4away
        data.loc[index, "diff_from_pos7away"] = diff_from_pos7away
        data.loc[index, "diff_from_pos18away"] = diff_from_pos18away
        
        data.loc[index, "difference"] = diff_from_opponent
        
        
        # Step #: Update team points based on match result
        if home_goals > away_goals:
            team_points[home_team] += 3  # Home team won, add 3 points
        elif home_goals < away_goals:
            team_points[away_team] += 3  # Away team won, add 3 points
        else:
            team_points[home_team] += 1  # It's a draw, add 1 point to both teams
            team_points[away_team] += 1
    
data = data[data["Round"] > 5]
data.drop(["HomeTeam","HomeGoals", "AwayTeam", "AwayGoals", "Round"], axis=1, inplace=True)   
data.drop(["HomeYellows", "HomeReds", "HomeSecondYellows", "AwayYellows", "AwayReds", "AwaySecondYellows"], axis=1, inplace=True)
# Display the updated DataFrame
#print(data)


#%%
# The splitting points for each Referee is 5 yellow cards and 0.25 red cards
YellowLimit, RedLimit = 5, 0.25
data["YellowRefCategory"] = [1 if x > YellowLimit else 0 for x in data["RefereeYellows"]]
data["RedRefCategory"] = [1 if x > RedLimit else 0 for x in data["RefereeReds"]]
data.drop(['Referee', 'RefereeYellows', 'RefereeReds'], axis=1, inplace=True)


data.fillna(data.mean().astype(int), inplace=True)


data["Yellows"] = [x + y for x,y in zip(data["Yellows"], data["secondYellows"])]
data["Reds"] = [x + y for x,y in zip(data["Reds"], data["secondYellows"])]

data.drop(["secondYellows"], axis=1, inplace=True)


final_data = data.copy()

# from sklearn.preprocessing import OneHotEncoder
# enc = OneHotEncoder()
# transformed = enc.fit_transform(data[["YellowRefCategory"]])
# final_data[enc.categories_[0]] = transformed.toarray()

# final_data = pd.get_dummies(data=final_data, columns=["YellowRefCategory", "RedRefCategory"])
# print(final_data.shape)

final_data.drop(["Reds"], axis=1, inplace=True)

Y = final_data["Yellows"]
X = final_data.drop(["Yellows"], axis=1)

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)


clf = RandomForestRegressor(random_state=9)

param_grid = {
    "n_estimators" : [50, 100, 200, 300],
    "max_depth" : [2, 3, 5]
    }

grid = GridSearchCV(estimator=clf, param_grid=param_grid, n_jobs=-1, verbose=2, cv=5)
grid.fit(X_train, Y_train)

grid.best_estimator_
results = grid.predict(X_test)
model_mse = mean_squared_error(Y_test, results)

baseline = np.repeat(5, len(results))
baseline_mse = mean_squared_error(Y_test, baseline)

"""




















