import pandas as pd
from flask import Flask, request, jsonify

app = Flask(__name__)
results = pd.read_csv('data.csv')

date = []
opponent = []
prediction = []

@app.route("/checkTeam", methods = ['POST'])
def showTeam():
    if request.method == 'POST':
        chosen_team = request.form['name']
    for _, x in results[results["Team"] == chosen_team].iterrows():
        date.append(x["Date"])
        opponent.append(x["Opponent"])
        if(x["prediction"] == 2):
            prediction.append('W')
        elif(x["prediction"] == 1):
            prediction.append('L')
        else:
            prediction.append('D')
    return jsonify(date = date, opponent = opponent, prediction = prediction)

if __name__ == "__main__": 
    app.run(debug=True)