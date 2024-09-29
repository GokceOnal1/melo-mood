from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import recommendation as backend
import nltk

# Download VADER lexicon for emotion analysis
nltk.download('vader_lexicon')

app = Flask(__name__)
app.secret_key = 'melomood.com'  # Use a secure and unpredictable secret key in production

@app.route("/")
def index():
    return render_template("index.html")

# Route for login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Extract data from the form
        username = request.form.get('username')
        password = request.form.get('password')

        # TODO: Add logic to handle login (e.g., check credentials)
        # For demonstration, we'll assume login is successful
        flash(f'Welcome back, {username}!', 'success')
        return redirect(url_for('render_recommendations_page'))  # Redirect to the /meloai route

    # If it's a GET request, render the login page
    return render_template('Login.html')


# Route for sign-up page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Process the form data
        username = request.form.get('username')
        email = request.form.get('email')  # Added email processing
        password = request.form.get('password')
        
        # TODO: Here you would typically save this data to a database
        # For demonstration, we'll assume signup is successful
        flash(f'Successfully signed up {username}!', 'success')
        return redirect(url_for('render_recommendations_page'))  # Redirect to the /meloai route
    
    return render_template('signup.html')


# Route to recommend music based on user's emotion
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

    # Get song recommendations based on the emotion
    try:
        recommendations = backend.filter_songs_by_emotion(emotion)
    except Exception as e:
        return jsonify({'error': f'Error getting song recommendations: {str(e)}'}), 500
        
    quote = backend.QUOTES.get(emotion, "Let the music flow through you.")
    # Return the quote and the recommendations
    print(recommendations)
    return render_template("result.html", quote=quote, recommendations=recommendations)

# Recommendations API Route
@app.route('/recommendations', methods=['GET'])
def recommendations_api():
    emotion = request.args.get('emotion')  # Get the emotion from the query parameters
    if not emotion:
        return jsonify({'error': 'Emotion parameter is missing.'}), 400

    # Fetch recommendations based on the emotion
    try:
        recommendations, random_quote = backend.filter_songs_by_emotion(emotion)
        return jsonify({
            'songs': recommendations,
            'quote': random_quote,
        })
    except Exception as e:
        return jsonify({'error': f'Error fetching recommendations: {str(e)}'}), 500


# Route to render recommendations page
@app.route('/get_recommendations_page', methods=['GET'])
def render_recommendations_page():
    return render_template('recommendations.html')


# Optional: Another Recommendations API Route (ensure unique name)
@app.route('/show_recommendations_page', methods=['GET'])
def show_recommendations_page():
    # Fetch recommendations from your logic (here it's just a placeholder)
    recommendations = []  # Fetch actual recommendations
    return render_template('recommendations.html', recommendations=recommendations)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
