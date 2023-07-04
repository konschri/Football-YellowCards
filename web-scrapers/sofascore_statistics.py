from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
import time
import csv


START = time.time()

""" Define the url of interest """ 
URL = "https://www.sofascore.com/tournament/football/spain/laliga/8"

""" Define the name of the league (used as partial name of the csv file that will contain the data) """
LEAGUE_NAME = "Spanish La Liga"

""" Pixels to scroll - Tune accordingly """
Y = 1150

""" Select year to extract through button click and scroll. N = 0 means current season, N = 1 last season etc. """
N = 1

## Instantiate the browser
options = Options()
options.page_load_strategy = 'eager'
# TODO this line does not prevent the website from reloading after 30 mins. Find alternative
profile = webdriver.FirefoxProfile()
profile.set_preference("dom.max_script_run_time", 0)

driver = webdriver.Firefox(options=options, firefox_profile=profile)
driver.maximize_window()
driver.get(URL)

## Press Consent Button
try:
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'fc-button.fc-cta-consent.fc-primary-button'))).click()
except:
    pass
time.sleep(3)


## Press the button to choose the season of interest based on N value
downshift = "downshift-1-item-"
downshift_string = downshift + str(N)
toggle_buttons = driver.find_elements_by_id("downshift-1-toggle-button")
toggle_buttons[-1].click()
#WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'downshift-1-toggle-button'))).click()
time.sleep(3)

season_clicks = driver.find_elements_by_id(downshift_string)
season_clicks[-1].click()
#WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, downshift_string))).click()
time.sleep(3)

## Store the season as a string in order to use it as the final part of the csv file that will contain the data
season = driver.find_elements_by_xpath("//div[@class='sc-fnGiBr kdHYZX']")[-1].text
season = season.replace("/", "_")
print(f"Season: {season}")

## Scroll based on Y value in order to reach the Matches Box
driver.execute_script("window.scrollTo(0, " + str(Y) + ")")
time.sleep(2)

## Click on the Group BY ROUND button 
driver.find_element_by_xpath("//div[normalize-space()='By Round']").click()
time.sleep(3)

## Open a csv file with certain header (the name is constructed based on `LEAGUE_NAME` and `season` variables)
csv_file = open(LEAGUE_NAME.replace(" ","") + season + "match_stats" + ".csv", "w", newline='')
csv_writer = csv.writer(csv_file, delimiter=',')

header = ["AwayAerialswon", "AwayBallpossession", "AwayDuelswon", "AwayFouls", "AwayInterceptions", "AwayPossessionlost", "AwayTackles",
          "AwayTeam",
          "Date",
          "HomeAerialswon", "HomeBallpossession", "HomeDuelswon", "HomeFouls", "HomeInterceptions", "HomePossessionlost", "HomeTackles",
          "HomeTeam",
          "Round"]

csv_writer.writerow(header)


## The main loop that will iterate over
# 1. Rounds
# 2. Games

while True:
    
    current_round = driver.find_element_by_css_selector("div[class='sc-hLBbgP sc-eDvSVe iozmdK ilXvf'] div[class='sc-fnGiBr kZMYN']").text
    print(f"Current round: {current_round}")
    matchbox = driver.find_element_by_class_name("sc-hLBbgP.hBOvkB")
    matches = matchbox.find_elements_by_tag_name("a")
    print(f"Matches: {len(matches)}")
    
    for i in range(1, len(matches)):
        
        ## Get the date of match
        try:
            #raw_date = matches[i].find_element_by_class_name("sc-hLBbgP.gudtvp").text
            raw_date = matches[i].find_element_by_class_name("sc-hLBbgP.iHLDa").text
            date = raw_date.split("\n")[0]
            gamestatus = raw_date.split("\n")[1]
        except:
            date, gamestatus = str(), str()
        
        if gamestatus != "FT":
            continue
        
        driver.execute_script("arguments[0].click();", matches[i])
        time.sleep(3)
        driver.execute_script("window.scrollTo(0, " + str(Y) + ")")
        time.sleep(2)
        
        ## Get the teams
        teams = driver.find_element_by_xpath("//span[@class='sc-bqWxrE XvCwv']")
        home_team, away_team = teams.text.split("-")[0], teams.text.split("-")[1]
        
        ## Instantiate a dictionary with 
        static_statistics = {"Round": current_round, 
                                     "Date": date,
                                     "HomeTeam": home_team.strip(),
                                     "AwayTeam": away_team.strip()}
        print(static_statistics)
        
        ## Click on the Statistics tab
        driver.find_element_by_xpath("//div[@data-tabid='Statistics']").click()
        
        
        ## Find the statistics that are useful for our task based on the Header defined before loop
        
        groups_of_stats = driver.find_elements_by_class_name("sc-hLBbgP.sc-eDvSVe.hknANX.hyKYsT")
        available_statistics = dict()
        
        for group in groups_of_stats:
            driver.execute_script("arguments[0].scrollIntoView(true);", group)
            rows_of_stats = group.find_elements_by_class_name("sc-hLBbgP.sc-eDvSVe.dSSyaL.bbcOkn")
            for row in rows_of_stats:
                elements = row.text.split("\n")
                feature = elements[1].replace(" ", "")
                if "Home"+feature in header: # This should be done in a more elegant way
                    available_statistics["Home"+feature], available_statistics["Away"+feature] = elements[0], elements[2]
        
        
        results = {key: available_statistics.get(key, static_statistics.get(key, -1)) for key in header}
        row = [results["AwayAerialswon"], results["AwayBallpossession"], results["AwayDuelswon"], results["AwayFouls"], results["AwayInterceptions"], results["AwayPossessionlost"], results["AwayTackles"], results["AwayTeam"],
          results["Date"],
          results["HomeAerialswon"], results["HomeBallpossession"], results["HomeDuelswon"], results["HomeFouls"], results["HomeInterceptions"], results["HomePossessionlost"], results["HomeTackles"],
          results["HomeTeam"], results["Round"]]
        csv_writer.writerow(row)
        
    ## Press previous button, if it fails we assume the we reached the first round thus we finished for this season
    try:
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, " + str(Y) + ")")
        # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "sc-bcXHqe.gvEXzS"))).click()
        time.sleep(3)
        buttons_previous_next = driver.find_elements_by_class_name("sc-bcXHqe.gvEXzS")
        #buttons_previous_next = driver.find_elements_by_class_name("sc-bqWxrE.kCrWFg")
        if buttons_previous_next[0].text.lower() == "previous":
            buttons_previous_next[0].click()
        else:
            csv_file.close()
            driver.close()
            break
    except Exception as e:
        csv_file.close()
        print(f"The following error occured: {e}")
            

print(f"Execution time for season {season} is {time.time() - START}")