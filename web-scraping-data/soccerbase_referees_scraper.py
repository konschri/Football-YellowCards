import numpy as np
import time
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd

base_url = 'https://www.soccerbase.com/referees/home.sd?tourn_id='

""" the league_ids are manually achieved while browsing at the website """
"""
=============>  14/15  |  15/16  |  16/17  |  17/18  |  18/19  |  19/20  |  20/21  | 
laliga       >  1397   |  1468   |  1513   |  1609   |  1679   |  1737   |  1818   |
epl          >  1386   |  1435   |  1501   |  1566   |  1635   |  1710   |  1797   |
bundesliga   >  1395   |  1462   |  1511   |  1597   |  1668   |  1725   |  1792   |
ligue1       >  1394   |  1461   |  1510   |  1596   |  1640   |  1738   |  1777   |
seriea       >  1396   |  1465   |  1512   |  1601   |  1672   |  1736   |  1817   |
rfpl         >  1381   |  1451   |  1537   |  1606   |  1676   |  1709   |  1783   |
"""


leagues = ['laliga', 'epl', 'bundesliga', 'ligue1', 'seriea', 'rfpl']
leagues_id_soccerbase = [[1397, 1468, 1513, 1609, 1679, 1737, 1818],
                         [1386, 1435, 1501, 1566, 1635, 1710, 1797],
                         [1395, 1462, 1511, 1597, 1668, 1725, 1792],
                         [1394, 1461, 1510, 1596, 1640, 1738, 1777],
                         [1396, 1465, 1512, 1601, 1672, 1736, 1817],
                         [1381, 1451, 1537, 1606, 1676, 1709, 1783]]

dictionary = {}
for idx, ele in enumerate(leagues_id_soccerbase):
    print('ele = ', ele)
    for ix, lid in enumerate(ele):
        url = base_url + str(lid)
        print(url)      
        
        if ix == 0: 
            inter_name = '14-15'
        elif ix == 1:
            inter_name = '15-16'
        elif ix == 2:
            inter_name = '16-17'
        elif ix == 3:
            inter_name = '17-18'
        elif ix == 4:
            inter_name = '18-19'
        elif ix == 5:
            inter_name = '19-20'
        elif ix == 6:
            inter_name = '20-21'
        
        res = requests.get(url)
        soup = BeautifulSoup(res.content, "html.parser")
        td = soup.find_all('td')
            
        """ get all the text from td's and store it in a list of strings
        also drop the last 2 elements since these are non valid info """
        
        items = []    
        for ele in td:
            items.append(ele.text)
            
        items = items[:-2]
        
        name_info = items[::5]
        from_info = items[1::5]
        ngames_info = items[2::5]
        yellow_info = items[3::5]
        red_info = items[4::5]
        
        fname = leagues[idx] + '_' + inter_name
        print(fname)
        
        dictionary[fname] = pd.DataFrame({'names': name_info,
                           'from': from_info,
                           'ngames': ngames_info,
                           'yellow': yellow_info,
                           'red': red_info,
                           'season': inter_name,
                           'league_info': fname
                           })
        

""" Concatenate the data of each dataframe and save as .csv """
final_df = pd.concat(dictionary.values(), ignore_index=True)
final_df.to_csv('referee_status_info.csv', index=False)
















