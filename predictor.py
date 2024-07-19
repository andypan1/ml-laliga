import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score

matches = pd.read_csv("matches.csv", index_col=0)

matches["Date"] = pd.to_datetime(matches["Date"])
matches["Venue_Code"] = matches["Venue"].astype("category").cat.codes
matches["Opp_Code"] = matches["Opponent"].astype("category").cat.codes
matches["Hour"] = matches["Time"].str.replace(":.+", "", regex = True).astype("int")
matches["Day_Code"] = matches["Date"].dt.dayofweek
matches["Target"] = matches["Result"].astype("category").cat.codes #D:0, L:1, W:2

future_matches = pd.read_csv("future_matches.csv", index_col=0)

future_matches["Date"] = pd.to_datetime(future_matches["Date"])
future_matches["Venue_Code"] = future_matches["Venue"].astype("category").cat.codes
future_matches["Opp_Code"] = future_matches["Opponent"].astype("category").cat.codes
future_matches["Day_Code"] = future_matches["Date"].dt.dayofweek
future_matches["Target"] = -99

rf = RandomForestClassifier(n_estimators=50, min_samples_split=10, random_state=1)
train = matches
test = future_matches
predictors = ["Venue_Code", "Opp_Code", "Day_Code"]
rf.fit(train[predictors], train["Target"])
preds = rf.predict(test[predictors])

acc = accuracy_score(test["Target"], preds)

combined = pd.DataFrame(dict(actual = test["Target"], prediction = preds))
# print(pd.crosstab(index = combined["actual"], columns=combined["prediction"])) for testing
# print(precision_score(test["Target"], preds, average='weighted')) for testing

def rolling_avg(group, cols, new_cols):
    group = group.sort_values("Date")
    rolling_stats = group[cols].rolling(3, min_periods=1, closed="left").mean()
    group[new_cols] = rolling_stats
    return group

cols = ["GF", "GA", "Sh", "SoT", "Dist", "FK", "PK", "PKatt"]
new_cols = [f"{c}_rolling" for c in cols]

for col in cols:
    if col not in future_matches.columns:
        future_matches[col] = 0

combined_matches = pd.concat([matches, future_matches], ignore_index=True)
combined_matches_rolling = combined_matches.groupby("Team").apply(lambda x: rolling_avg(x, cols, new_cols))
combined_matches_rolling = combined_matches_rolling.droplevel("Team")
combined_matches_rolling.index = range(combined_matches_rolling.shape[0])
combined_matches_rolling.to_csv("h.csv") #for debugging


def make_predict(matches, predictors):
    train = matches[matches["Date"] < '2024-08-01']
    test = matches[matches["Date"] >= '2024-08-01']
    rf.fit(train[predictors], train["Target"])
    preds = rf.predict(test[predictors])
    combined = pd.DataFrame(dict(actual = test["Target"], prediction = preds))
    precision = precision_score(test["Target"], preds, average='weighted')
    return combined, precision 

combined, precision = make_predict(combined_matches_rolling, predictors + new_cols)
combined = combined.merge(combined_matches_rolling[["Date", "Team", "Opponent", "Result"]], left_index=True, right_index=True)

# class MissDict(dict):
#     __missing__ = lambda self, key: key

# map_values = {
#     ""
# }
# mapping = MissDict(**map_values)
# combined["new_team"] = combined["Team"].map(mapping)

merged = combined.merge(combined, left_on = ["Date", "Team"], right_on = ["Date", "Opponent"])
merged.to_csv("lol.csv")
print(merged)
print(merged[(merged["prediction_x"] == 2) & (merged["prediction_y"] == 1)]["actual_x"].value_counts())
print(merged[(merged["prediction_x"] == 1) & (merged["prediction_y"] == 2)]["actual_x"].value_counts())
print(merged[(merged["prediction_x"] == 0) & (merged["prediction_y"] == 0)]["actual_x"].value_counts())

