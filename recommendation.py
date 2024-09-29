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
nltk.download('vader_lexicon')

# Load environment variables
load_dotenv()

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
    'positive': "Music is the voice of the soul, and today it's singing just for you.",
    'neutral': "Let the music play, and let it carry you through the moment.",
    'negative': "Sometimes, music is the best therapy. Let these tunes heal your heart."
}

# Emotion-based energy thresholds (for simplicity)
EMOTION_MAP = {
    'positive': 0.7,  # High energy for positive emotions
    'neutral': 0.5,   # Medium energy for neutral emotions
    'negative': 0.3   # Low energy for negative emotions
}


def get_recommendations(track_name, num_recommendations=10):
    try:
        # Get index of the track
        idx = music_indices[track_name][0]
    except KeyError:
        return []

    # Get similarity scores for the song
    sim_scores = list(enumerate(cos_similar[idx]))  # Get similarity scores for the song
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)  # Sort the songs by similarity

    # Select top similar songs
    sim_scores = sim_scores[1:num_recommendations + 1]

    # Randomize the top similar songs for variety
    random.shuffle(sim_scores)  # Shuffle the similar songs to add randomness

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

    return filtered_songs[['track_name', 'artist_name', 'energy']].to_dict(orient='records')
