from flask import *
from flask import Flask
from flask import render_template
import recommendation as backend

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route('/recommend', methods=['GET'])
def recommend():
    track_name = request.args.get('track_name')  # Get the track name from the query parameter
    recommendations = backend.get_recommendations(track_name)
    return recommendations
    # print(recommendations)
    # return recommendations
