import pandas as pds
from flask import Flask, request, jsonify
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from dotenv import load_dotenv
import os
from nltk.sentiment.vader import SentimentIntensityAnalyzer  # For sentiment analysis
import random
import nltk
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

nltk.download('vader_lexicon')

# Load environment variables from .env file
load_dotenv()

# Spotify API credentials (consider loading from .env for security)
client_id = os.getenv('SPOTIFY_CLIENT_ID', '0def6d0090714b48a41e8cd9dc62bcfa')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET', '6016dfd9269f4bf79daf475bfbb76622')

# Authenticate with Spotify
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def search_spotify(song_name):
    results = sp.search(q=song_name, type='track', limit=1)
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        return {
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'url': track['external_urls']['spotify']
        }
    return None

# Load the dataset
songs_data = pds.read_csv("data/tcc_ceds_music.csv")

# Fill any missing lyrics with an empty string
songs_data['lyrics'] = songs_data['lyrics'].fillna("")

# Use TfidfVectorizer to analyze the lyrics
vtf = TfidfVectorizer(stop_words='english')
music_vector_matrix = vtf.fit_transform(songs_data['lyrics'])

# Calculate cosine similarity based on the lyrics
cos_similar = linear_kernel(music_vector_matrix, music_vector_matrix)

# Create a Series to map track names to indices
music_indices = pds.Series(songs_data.index, index=songs_data['track_name']).drop_duplicates()

# Initialize sentiment analyzer
sent_analyzer = SentimentIntensityAnalyzer()

# Pre-defined quotes to display based on emotion
QUOTES = {
    'positive': ["Music is the voice of the soul, and today it's singing just for you.", 
                 "Feel the joy in every note and let it fill your heart."],
    'neutral': ["Let the music play, and let it carry you through the moment.", 
                "In the middle of every difficulty lies an opportunity for harmony."],
    'negative': ["Sometimes, music is the best therapy. Let these tunes heal your heart.", 
                 "Even in the darkest times, music can bring light."],
    'excited': ["Let the beat drop and the energy flow!", 
                "Get ready to feel the rush of energy with these tunes!"],
    'sad': ["In the quiet moments, music can be a gentle friend.", 
            "These songs are here to soothe your soul."],
    'anxious': ["Take a deep breath; let the music calm your mind.", 
                "Let the music wash away your worries."],
    'angry': ["Let the music be your outlet; release the energy.", 
              "Channel your emotions through these powerful tracks."],
    'happy': ["Joy is in the air; let the music lift you higher!", 
              "Celebrate your happiness with these uplifting tunes!"]
}

# Emotion-based energy thresholds (for simplicity)
EMOTION_MAP = {
    'positive': 0.7,
    'neutral': 0.5,
    'negative': 0.3,
    'happy': 0.75,
    'sad': 0.25,
    'angry': 0.4,
    'anxious': 0.3,
    'excited': 0.8,
}

def get_recommendations(track_name, num_recommendations=10):
    try:
        # Get index of the track
        idx = music_indices[track_name]
    except KeyError:
        return []

    # Get similarity scores for the song
    sim_scores = list(enumerate(cos_similar[idx]))  # Get similarity scores for the song
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)  # Sort by similarity

    # Select top similar songs
    sim_scores = sim_scores[1:num_recommendations + 1]

    # Randomize the top similar songs for variety
    random.shuffle(sim_scores)

    # Get indices of the recommended songs
    sim_index = [i[0] for i in sim_scores]
    dataframe = songs_data.iloc[sim_index][['track_name', 'artist_name', 'lyrics', 'energy']]

    # Convert DataFrame to a list of dictionaries
    return dataframe[['track_name', 'artist_name', 'energy']].to_dict(orient='records')


def analyze_emotion(user_input):
    """
    Analyze the sentiment of the user's input and classify it into an emotion category.
    """
    scores = sent_analyzer.polarity_scores(user_input)
    if scores['compound'] >= 0.05:
        return 'positive'
    elif scores['compound'] <= -0.05:
        return 'negative'
    else:
        return 'neutral'


def filter_songs_by_emotion(emotion, num_recommendations=10):
    """
    Recommend songs based on the detected emotion by filtering the dataset.
    """
    energy_threshold = EMOTION_MAP.get(emotion, 0.5)

    # Filter songs by energy level based on the user's emotion
    filtered_songs = songs_data[songs_data['energy'] >= energy_threshold]

    # Randomly shuffle the filtered songs
    filtered_songs = filtered_songs.sample(frac=1).head(num_recommendations)  # Randomize and pick top N

    # Prepare the output with URLs for Spotify
    recommendations = []
    for _, row in filtered_songs.iterrows():
        recommendations.append({
            'track_name': row['track_name'],
            'artist_name': row['artist_name'],
            'energy': row['energy'],
            'url': f"https://open.spotify.com/search/{row['track_name']}%20{row['artist_name']}"  # Construct the Spotify URL
        })

    # Select a random quote based on the user's emotion
    random_quote = random.choice(QUOTES.get(emotion, ["Let the music flow through you."]))
    
    return recommendations, random_quote
