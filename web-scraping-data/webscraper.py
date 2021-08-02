import numpy as np
import time
import requests
from bs4 import BeautifulSoup
import csv
import json
import pandas as pd


base_url = "https://understat.com/match"
match_id = "5499"
url = base_url + "/" + match_id

response = requests.get(url)
cont = response.content

results_dictionary = {}

soup = BeautifulSoup(cont, "html.parser")
scripts = soup.find_all('script')
print(scripts)

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
cards = (n_yellow, n_red)


# retrieve team ids
for key, value in data['h'].items():
    h_team_id = value.get('team_id')
    if h_team_id: break
        
for key, value in data['a'].items():
    a_team_id = value.get('team_id')
    if a_team_id: break
teams = (h_team_id, a_team_id)


# retrieve match date
strings_shotsData = scripts[1].string
ind_start = strings_shotsData.index("('") + 2
ind_end = strings_shotsData.index("')")
json_data = strings_shotsData[ind_start:ind_end]
json_data = json_data.encode('utf').decode('unicode_escape')
data = json.loads(json_data)

date = data['h'][0]['date']
print(date)

results_dictionary[match_id] = [cards, teams, date]

print(results_dictionary)
