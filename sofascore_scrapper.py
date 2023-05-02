from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
import warnings
import time
import csv



class SofaScoreScraper():
    
    def __init__(self, url, league_name, season_code):
        self.url = url
        self.league_name = league_name
        self.Y = 1150
        self.N = season_code
        
        self.options = Options()
        self.options.set_preference('log.level', 0)
        self.options.page_load_strategy = 'eager'
        
        self.profile = webdriver.FirefoxProfile()
        self.profile.set_preference("accessibility.blockautorefresh", True)
        
        self.driver = webdriver.Firefox(options=self.options, firefox_profile=self.profile)
        self.driver.maximize_window()
        
        
    def navigate_to_season(self):
        warnings.filterwarnings("ignore", category=UserWarning, module='selenium.webdriver')
        self.driver.get(self.url)

        # Press Consent
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'fc-button.fc-cta-consent.fc-primary-button'))).click()
        except:
            pass
        time.sleep(3)
        
        
        downshift = "downshift-0-item-"
        downshift_string = downshift + str(self.N)       
            
        # add comment
        #toggle_buttons = self.driver.find_elements_by_id("downshift-1-toggle-button")
        #toggle_buttons[-1].click()
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'downshift-0-toggle-button'))).click()
        time.sleep(3)
        
        # add comment
        #season_clicks = self.driver.find_elements_by_id(downshift_string)
        #season_clicks[-1].click()
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, downshift_string))).click()
        time.sleep(3)
        
        season = self.driver.find_elements_by_xpath("//div[@class='sc-fnGiBr kdHYZX']")[-1].text
        season = season.replace("/", "_")
        print(f"Season: {season}")
        
        return season
        
    
    def select_sort_by_round(self):
        # add comment
        self.driver.execute_script("window.scrollTo(0, " + str(self.Y) + ")")
        time.sleep(2)
        
        # add comment    
        self.driver.find_element_by_xpath("//div[normalize-space()='By Round']").click()
        time.sleep(3)
        
    def create_csv(self, season):
        csv_file = open(self.league_name.replace(" ","") + season + ".csv", "w", newline='')
        csv_writer = csv.writer(csv_file, delimiter=',')
        header = ["Round", "Date", "HomeTeam", "HomeYellows", "HomeReds", "HomeSecondYellows", "AwayTeam", "AwayYellows", "AwayReds", "AwaySecondYellows",
                  "Referee", "RefereeYellows", "RefereeReds", "Stadium", "Location", "Attendance"]
        csv_writer.writerow(header)
        return csv_file, csv_writer
        
    
    def main(self, csv_file, csv_writer):
        while True:
    
            current_round = self.driver.find_element_by_css_selector("div[class='sc-hLBbgP sc-eDvSVe iozmdK ilXvf'] div[class='sc-fnGiBr kZMYN']").text
        
            matchbox = self.driver.find_element_by_class_name("sc-hLBbgP.hBOvkB")
            matches = matchbox.find_elements_by_tag_name("a")
            
            for i in range(1, len(matches)):
                
                # Get the date of match
                try:
                    raw_date = matches[i].find_element_by_class_name("sc-hLBbgP.gudtvp").text
                    date = raw_date.split("\n")[0]
                    gamestatus = raw_date.split("\n")[1]
                except:
                    date, gamestatus = str(), str()
                
                if gamestatus != "FT":
                    continue
                    
                self.driver.execute_script("arguments[0].click();", matches[i])
                time.sleep(3)
                self.driver.execute_script("window.scrollTo(0, " + str(self.Y) + ")")
                time.sleep(2)
                
                # Get the teams
                teams = self.driver.find_element_by_xpath("//span[@class='sc-bqWxrE XvCwv']")
                home_team, away_team = teams.text.split("-")[0], teams.text.split("-")[1]
                
                # Get the data that u want
                infobox = self.driver.find_element_by_class_name("sc-hLBbgP.sc-hBxehG.ksVQpa.dIKVzc.ps.ps--active-y")
                
                # cards
                try:
                    moments_box = infobox.find_element_by_class_name("sc-hLBbgP.etIUTK")
                    left_column_moments = moments_box.find_elements_by_class_name("sc-hLBbgP.sc-eDvSVe.guJEBJ.dAJeXv")
                    right_column_moments = moments_box.find_elements_by_class_name("sc-hLBbgP.sc-eDvSVe.guJEBJ.fSvOom")
        
                    home_yellow_cards, home_red_cards, home_second_yellow_cards = 0, 0, 0
                    away_yellow_cards, away_red_cards, away_second_yellow_cards = 0, 0, 0
                except:
                    home_yellow_cards, home_red_cards, home_second_yellow_cards = -1, -1, -1
                    away_yellow_cards, away_red_cards, away_second_yellow_cards = -1, -1, -1
                    left_column_moments, right_column_moments = [], []
                    
                
                for moment in left_column_moments:
                    try:
                        titletag = moment.find_element_by_css_selector("svg>title")
                        titletext = titletag.get_attribute("innerHTML")
                    except:
                        continue
                    if titletext == "Yellow card":
                        home_yellow_cards += 1
                    elif titletext == "Red card":
                        home_red_cards += 1
                    elif titletext == "2nd Yellow card (Red)":
                        home_second_yellow_cards +=1
                    else:
                        continue
                
                for moment in right_column_moments:
                    try:
                        titletag = moment.find_element_by_css_selector("svg>title")
                        titletext = titletag.get_attribute("innerHTML")
                    except:
                        continue
                    if titletext == "Yellow card":
                        away_yellow_cards += 1
                    elif titletext == "Red card":
                        away_red_cards += 1
                    elif titletext == "2nd Yellow card (Red)":
                        away_second_yellow_cards +=1
                    else:
                        continue
                
                
                # ref + venue [-1] because after some seasons there is another subtable "Odds" on same class
                referee_venue_box = infobox.find_elements_by_class_name("sc-hLBbgP.czcKUi")[-1]
                self.driver.execute_script("arguments[0].scrollIntoView(true);", referee_venue_box)
                
                #inner_referee_venue_box = referee_venue_box.find_elements_by_class_name("sc-hLBbgP.dRtNhU.sc-ca17568b-0.gHnyhj") # this class name seemed to changed during developing
                inner_referee_venue_box = referee_venue_box.find_elements_by_class_name("sc-hLBbgP.dRtNhU.sc-5d1cf382-0.coeTae")
                
                
                # first info for referees
                try:
                    referee_box = inner_referee_venue_box[0]
                    referee_name = referee_box.find_element_by_xpath(".//span[@class='sc-bqWxrE gOBUVT']").text
                    
                    try:
                        referee_cards = referee_box.find_elements_by_class_name("sc-hLBbgP.sc-eDvSVe.brVQfn.bbcOkn")[-1]
                        inner_referee_cards = referee_cards.find_element_by_class_name("sc-hLBbgP.sc-eDvSVe.gjJmZQ.fRddxb").text
                        referee_reds = inner_referee_cards.split("\n")[0]
                        referee_yellows = inner_referee_cards.split("\n")[1]
                    except:
                        referee_reds, referee_yellows = str(), str()
                except:
                    referee_name, referee_reds, referee_yellows = str(), str(), str()
                
                # second info for venue
                try:
                    venue_box = inner_referee_venue_box[1]
                    try:
                        venue_first_row = venue_box.find_elements_by_class_name("sc-hLBbgP.sc-eDvSVe.brVQfn.bbcOkn")[0]
                        venue_name = venue_first_row.find_elements_by_class_name("sc-bqWxrE.kAIqxV")[-1].text
                    except:
                        venue_name = str()
                    
                    try:
                        venue_second_row = venue_box.find_elements_by_class_name("sc-hLBbgP.sc-eDvSVe.brVQfn.bbcOkn")[1]
                        venue_location = venue_second_row.find_element_by_class_name("sc-bqWxrE.ksXgHo").text
                    except:
                        venue_location = str()
                        
                    try:
                        venue_third_row = venue_box.find_elements_by_class_name("sc-hLBbgP.sc-eDvSVe.brVQfn.bbcOkn")[2]
                        venue_attendance = venue_third_row.find_elements_by_class_name("sc-bqWxrE.kAIqxV")[-1].text
                    except:
                        venue_attendance = str()
                except:
                    venue_name, venue_location, venue_attendance = str(), str(), str()
                
           
                print(f"Round: {current_round} - Date: {date}")
                print(f"Teams: {home_team} - {away_team}")
                print(f"Team: {home_team} received {home_yellow_cards} Yellow cards - {home_red_cards} Red cards and {home_second_yellow_cards} Second Yellows")
                print(f"Team: {away_team} received {away_yellow_cards} Yellow cards - {away_red_cards} Red cards and {away_second_yellow_cards} Second Yellows")
                print(f"Referee_name: {referee_name}")
                print(f"Rerefee_stats: red cards {referee_reds}, yellow cards {referee_yellows}")
                print(f"Stadium: {venue_name} - Location {venue_location}")
                print(f"Attendance: {venue_attendance}")
                print("\n\n")
                
                results = [current_round, date, home_team.strip(), home_yellow_cards, home_red_cards, home_second_yellow_cards, away_team.strip(), away_yellow_cards, away_red_cards, away_second_yellow_cards,
                            referee_name, referee_yellows, referee_reds, venue_name, venue_location, venue_attendance]
                csv_writer.writerow(results)
                
            #press previous button, if it fails we assume the we reached the first round thus we finished for this season
            try:
                #WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "sc-bcXHqe.gvEXzS"))).click()
                time.sleep(3)
                buttons_previous_next = self.driver.find_elements_by_class_name("sc-bcXHqe.gvEXzS")
                if buttons_previous_next[0].text.lower() == "previous":
                    buttons_previous_next[0].click()
                else:
                    csv_file.close()
                    self.driver.close()
                    break
            except Exception as e:
                csv_file.close()
                print(f"The following error occured: {e}")
    
    def scrape(self):
        season = self.navigate_to_season()
        self.select_sort_by_round()
        csv_file, csv_writer = self.create_csv(season)
        self.main(csv_file, csv_writer)
        
          