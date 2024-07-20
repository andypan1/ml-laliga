import pandas as pd
from flask import Flask, request

app = Flask(__name__)
results = pd.read_csv('data.csv')


date = []
opponent = []
prediction = []

@app.route("/")
def showTeam():
    if request.method == 'POST':
        chosen_team = request.form['team']
    for _, x in results[results["Team"] == chosen_team].iterrows():
        date.append(x["Date"])
        opponent.append(x["Opponent"])
        if(x["prediction"] == 2):
            prediction.append('W')
        elif(x["prediction"] == 1):
            prediction.append('L')
        else:
            prediction.append('D')

if __name__ == "__main__": 
    app.run(debug=True)