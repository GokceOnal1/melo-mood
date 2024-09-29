from flask import *
from flask import Flask
from flask import render_template
import recommendation as backend
import nltk
nltk.download('vader_lexicon')
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/meloai")
def meloai():
    return render_template("bot.html")

@app.route('/recommend', methods=['GET'])
def recommend_music():
    user_input = request.args.get('emotion')

    # Check if user_input is provided, else return an error message
    if user_input is None or user_input.strip() == "":
        return jsonify({
            'error': 'Emotion input is missing. Please provide your emotion.'
        }), 400

    # Analyze the user's emotion
    try:
        emotion = backend.analyze_emotion(user_input)
    except Exception as e:
        return jsonify({'error': f'Error analyzing emotion: {str(e)}'}), 500

    # Select an appropriate quote
    quote = backend.QUOTES.get(emotion, "Let the music flow through you.")
    
    # Get song recommendations based on the emotion
    try:
        recommendations = backend.filter_songs_by_emotion(emotion)
    except Exception as e:
        return jsonify({'error': f'Error getting song recommendations: {str(e)}'}), 500

    # Return the quote and the recommendations
    return jsonify({
        'quote': quote,
        'recommendations': recommendations
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)