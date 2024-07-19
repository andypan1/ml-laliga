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

rf = RandomForestClassifier(n_estimators=50, min_samples_split=10, random_state=1)
train = matches[matches["Date"] < '2024-01-01'] 
test = matches[matches["Date"] > '2024-01-01'] 
predictors = ["Venue_Code", "Opp_Code", "Hour", "Day_Code"]
rf.fit(train[predictors], train["Target"])
preds = rf.predict(test[predictors])

acc = accuracy_score(test["Target"], preds)

combined = pd.DataFrame(dict(actual = test["Target"], prediction = preds))
print(pd.crosstab(index = combined["actual"], columns=combined["prediction"]))
print(precision_score(test["Target"], preds, average='weighted'))

def rolling_avg(group, cols, new_cols):
    group = group.sort_values("Date")
    rolling_stats = group[cols].rolling(3, closed="left").mean()
    group[new_cols] = rolling_stats
    group = group.dropna(subset = new_cols)
    return group

cols = ["GF", "GA", "Sh", "SoT", "Dist", "FK", "PK", "PKatt"]
new_cols = [f"{c}_rolling" for c in cols]
matches_rolling = matches.groupby("Team").apply(lambda x: rolling_avg(x, cols, new_cols))
matches_rolling = matches_rolling.droplevel("Team")
matches_rolling.index = range(matches_rolling.shape[0])

def make_predict(matches, predictors):
    train = matches[matches["Date"] < '2024-01-01'] 
    test = matches[matches["Date"] > '2024-01-01'] 
    rf.fit(train[predictors], train["Target"])
    preds = rf.predict(test[predictors])
    combined = pd.DataFrame(dict(actual = test["Target"], prediction = preds))
    precision = precision_score(test["Target"], preds, average='weighted')
    return combined, precision 

combined, precision = make_predict(matches_rolling, predictors + new_cols)
combined = combined.merge(matches_rolling[["Date", "Team", "Opponent", "Result"]], left_index=True, right_index=True)

# class MissDict(dict):
#     __missing__ = lambda self, key: key

# map_values = {
#     ""
# }
# mapping = MissDict(**map_values)
# combined["new_team"] = combined["Team"].map(mapping)

merged = combined.merge(combined, left_on = ["Date", "Team"], right_on = ["Date", "Opponent"])
print(merged[(merged["prediction_x"] == 2) & (merged["prediction_y"] == 1)]["actual_x"].value_counts())

