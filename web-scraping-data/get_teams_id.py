import numpy as np
import time
import requests
from bs4 import BeautifulSoup
import csv
import json
import pandas as pd


base_url = 'https://understat.com/league'
leagues = ['La_liga', 'EPL', 'Bundesliga', 'Serie_A', 'Ligue_1', 'RFPL']
seasons = ['2014', '2015', '2016', '2017', '2018']

teams = {}
for ele in seasons:
    url = base_url + '/' + leagues[0] + '/' + ele

    res = requests.get(url)
    soup = BeautifulSoup(res.content, "html.parser")
    scripts = soup.find_all('script')

    string_with_json_obj = ''

    # Find data for teams
    for el in scripts:
        if 'teamsData' in str(el):
            string_with_json_obj = str(el).strip()   

    # strip unnecessary symbols and get only JSON data
    ind_start = string_with_json_obj.index("('")+2
    ind_end = string_with_json_obj.index("')")
    json_data = string_with_json_obj[ind_start:ind_end]
    json_data = json_data.encode('utf8').decode('unicode_escape')
    data = json.loads(json_data)
    
    for id in data.keys():
        teams[id] = data[id]['title']