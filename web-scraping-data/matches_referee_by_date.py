import csv
import time
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import selenium
from selenium import webdriver

base_url = 'https://www.soccerbase.com/matches/results.sd?date='

# Assign the dates in format of %Y-%m-%d
start_date = '2014-09-11'
end_date = '2014-09-13'

Drange = pd.date_range(start=start_date, end=end_date).to_pydatetime().tolist()
Date_rangeOI = []
for day in Drange:
    day = day.strftime("%Y-%m-%d")
    Date_rangeOI.append(day)

csv_file = open("soccerbaseData.csv", "w", newline='')
csv_writer = csv.writer(csv_file, delimiter=',')

for date in Date_rangeOI:
    url = base_url + date
    
    driver = webdriver.Firefox()
    driver.get(url)

    elements = driver.find_elements_by_class_name('score')
    results = [date]
    for elem in elements:
        elem.click()
        start_time = time.time()
        
        html_source = driver.page_source
        soup = BeautifulSoup(html_source)
        
        match_data = soup.find("div", {"class", "rpBubbleContent"})
        
        # Check if data are available
        unavailable = match_data.find("div", {"class": "nodataBlock"})
        if unavailable:
            continue
        
        data = match_data.find_all("dd")
        for el in data:
            results.append(el.get_text())
            print(el.get_text())
        
        # Get data through html classes
        teamA = soup.find_all("th", {"class", "right"})[-1].get_text() 
        teamB = soup.find_all("th", {"class", "left"})[-1].get_text()
        results.append(teamA)
        results.append(teamB)
        print(teamA, teamB)
        

        end_time = time.time()
        retrieval_duration = end_time - start_time
        results.append(retrieval_duration)
        print('####'*10)
        print('Time: ', retrieval_duration)
        csv_writer.writerow(results)
        results = [date]
        # In case we need to slow down the process
        #time.sleep(5)

csv_file.close()

