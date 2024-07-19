import requests
import time
import pandas as pd
from bs4 import BeautifulSoup

standings_url = "https://fbref.com/en/comps/12/La-Liga-Stats"
years = list(range(2025, 2020, -1))
all_matches = []
for year in years:
    data = requests.get(standings_url)
    soup = BeautifulSoup(data.text)
    standings = soup.select('table.stats_table')[0] #filter only the standings table

    links = [l.get("href") for l in standings.find_all('a')] #find all links
    links = [l for l in links if '/squads' in l] #filter links to only team links
    team_urls = [f"https://fbref.com{l}" for l in links] #convert to links

    previous_season = soup.select("a.prev")[0].get("href")
    standings_url = f"https://fbref.com/{previous_season}"

    for url in team_urls:
        name = url.split("/")[-1].replace("-Stats", "").replace("-", " ")
        data = requests.get(url)
        matches = pd.read_html(data.text, match = "Scores & Fixtures")[0]

        #scrape shooting stats
        soup = BeautifulSoup(data.text)
        links = [l.get("href") for l in soup.find_all('a')]
        links = [l for l in links if l and 'all_comps/shooting/' in l]
        data = requests.get(f"https://fbref.com{links[0]}")
        shooting = pd.read_html(data.text, match = "Shooting")[0]
        shooting.columns = shooting.columns.droplevel()

        try:
            team_data = matches.merge(shooting[["Date", "Sh", "SoT", "Dist", "FK", "PK", "PKatt"]])
        except ValueError:
            continue

        team_data = team_data[team_data["Comp"] == "La Liga"]
        team_data["Season"] = year
        team_data["Team"] = name
        all_matches.append(team_data)
        time.sleep(10)

match_df = pd.concat(all_matches)
match_df.to_csv("matches.csv")

next_season_url = "https://fbref.com/en/comps/12/2024-2025/2024-2025-La-Liga-Stats"
data = requests.get(next_season_url)
soup = BeautifulSoup(data.text)
standings = soup.select('table.stats_table')[0] 
links = [l.get("href") for l in standings.find_all('a')] 
links = [l for l in links if '/squads' in l] 
team_urls = [f"https://fbref.com{l}" for l in links] 
all_matches = []
for url in team_urls:
    name = url.split("/")[-1].replace("-Stats", "").replace("-", " ")
    data = requests.get(url)
    matches = pd.read_html(data.text, match = "Scores & Fixtures")[0]
    matches = matches[matches["Comp"] == "La Liga"]
    matches["Season"] = year
    matches["Team"] = name
    all_matches.append(matches)
    time.sleep(4)

future_match_df = pd.concat(all_matches)
future_match_df.to_csv("future_matches.csv")

