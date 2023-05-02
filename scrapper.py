from sofascore_scrapper import SofaScoreScraper
import argparse


usage = """\nThis script uses selenium to scrape data regarding yellow cards from the SofaScore website.
The codification of the selected season follows a simple rule 0 = current season, 1 = last season, ..., 5 = five seasons ago \n\n"""

# Define the command line arguments
parser = argparse.ArgumentParser(usage=usage)
parser.add_argument('url', type=str, help='the URL to process')
parser.add_argument('league_name', type=str, help='the name of the league')
parser.add_argument('season_code', type=int, help='the integer to process')

# Parse the command line arguments
#args = parser.parse_args()
args, unknown = parser.parse_known_args()
url, league_name, season_code = args.url, args.league_name, args.season_code

# Print the user input
print("You entered the following:")
print("URL: " + args.url)
print("League name: " + args.league_name)
print("Season code: " + str(args.season_code))


# url = "https://www.sofascore.com/tournament/football/spain/laliga/8"
# league_name = "Spanish La Liga"
# season_code = 5

scrpr = SofaScoreScraper(url, league_name, season_code)
scrpr.scrape()