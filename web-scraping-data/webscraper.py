import numpy as np
import time
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd


START_TIME = time.time()

base_url = "https://understat.com/match"

start_match_id = 1
total_match_id = 100
match_ids_range = list(range(start_match_id, total_match_id+1))
match_ids = list(map(str, match_ids_range))


# Initialize the dictionaries to store results for each of the 6 available categories
laliga_dict = {}
epl_dict = {}
bundesliga_dict = {}
seriea_dict = {}
ligue1_dict = {}
rfpl_dict = {}


for match_id in match_ids:
    
    """   create the url to call   """ 
    url = base_url + "/" + match_id 
    
    """   Get scripts based on the given url   """
    res = requests.get(url)
    soup = BeautifulSoup(res.content, "html.parser")
    scripts = soup.find_all('script')
    
    """   avoid 404 error that returns empty list   """ 
    if not scripts:
        continue
    
    """    Get DATE and LEAGUE NAME - league name is required to iterate through user given match ids   """
    strings = scripts[1].string
    
    ind_start = strings.index("match_info")+26 # TODO: adjust to acquire info in a more elegant way
    ind_end = len(strings)-4
    json_data = strings[ind_start:ind_end]
    json_data = json_data.encode('utf').decode('unicode_escape')
    data = json.loads(json_data)
    
    date = data['date']
    league_name = data['league']
    
    """    Get YELLOW and RED cards as well as TEAM_IDs for the specific match id   """
    strings = scripts[2].string
    ind_start = strings.index("('")+2
    ind_end = strings.index("')")
    json_data = strings[ind_start:ind_end]
    json_data = json_data.encode('utf').decode('unicode_escape')
    data = json.loads(json_data)
    
    # retrieve cards data
    n_yellow, n_red = 0, 0
    for key, value in data['h'].items():
        n_yellow += int(value.get('yellow_card'))
        n_red += int(value.get('red_card'))
    for key, value in data['a'].items():
        n_yellow += int(value.get('yellow_card'))
        n_red += int(value.get('red_card'))
    #cards = (n_yellow, n_red)
    
    
    # retrieve team ids
    for key, value in data['h'].items():
        h_team_id = value.get('team_id')
        if h_team_id: break
            
    for key, value in data['a'].items():
        a_team_id = value.get('team_id')
        if a_team_id: break
    #teams = (h_team_id, a_team_id)
    
    if league_name == 'EPL':
        epl_dict[match_id] = [n_yellow, n_red, h_team_id, a_team_id, date, league_name] # maybe get rid of league_name
    elif league_name == 'La liga':
        laliga_dict[match_id] = [n_yellow, n_red, h_team_id, a_team_id, date, league_name]
    elif league_name == 'Bundesliga':
        bundesliga_dict[match_id] = [n_yellow, n_red, h_team_id, a_team_id, date, league_name]
    elif league_name == 'Serie A':
        seriea_dict[match_id] = [n_yellow, n_red, h_team_id, a_team_id, date, league_name]
    elif league_name == 'Ligue 1':
        ligue1_dict[match_id] = [n_yellow, n_red, h_team_id, a_team_id, date, league_name]
    elif league_name == 'RFPL':
        rfpl_dict[match_id] = [n_yellow, n_red, h_team_id, a_team_id, date, league_name]
    else:
        print('league_name error - skip match_id: ', match_id)
        continue

df_epl = pd.Series(epl_dict).to_frame().reset_index()
df_laliga = pd.Series(laliga_dict).to_frame().reset_index()
df_bundesliga = pd.Series(bundesliga_dict).to_frame().reset_index()
df_seriea = pd.Series(seriea_dict).to_frame().reset_index()
df_ligue1 = pd.Series(ligue1_dict).to_frame().reset_index()
df_rfpl = pd.Series(rfpl_dict).to_frame().reset_index()

league_dataframes = [df_epl, df_laliga, df_bundesliga, df_seriea, df_ligue1, df_rfpl]
for ele in league_dataframes:
    #ele.columns = ['Match_ID', 'n_Yellow', 'n_Red', 'h_Team_ID', 'a_Team_ID' , 'Date', 'League_Name']
    ele.columns = ['Match_ID', 'Data']

END_TIME = time.time()
print('Total execution time in minutes: ', round(END_TIME-START_TIME)/60)

# TODO: save dataframes to csv files








