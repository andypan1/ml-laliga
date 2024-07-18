import pandas as pd

matches = pd.read_csv("matches.csv", index_col=0)

matches["Date"] = pd.to_datetime(matches["Date"])
matches["Venue_Code"] = matches["Venue"].astype("category").cat.codes
matches["Opp_Code"] = matches["Opponent"].astype("category").cat.codes
matches["Hour"] = matches["Time"].str.replace(":.+", "", regex = True).astype("int")
matches["Day_Code"] = matches["Date"].dt.dayofweek


print(matches)