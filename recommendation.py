import pandas as pds
from flask import Flask, request, jsonify
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from dotenv import load_dotenv
import os

#http://127.0.0.1:5000/recommend?track_name=Mercy

songs_data = pds.read_csv("data\\tcc_ceds_music.csv")

load_dotenv()

vtf = TfidfVectorizer(stop_words='english')
songs_data['lyrics'] = songs_data['lyrics'].fillna("")
music_vector_matrix = vtf.fit_transform(songs_data['lyrics'])

cos_similar = linear_kernel(music_vector_matrix, music_vector_matrix)

music_indices = pds.Series(songs_data.index, index=songs_data['track_name']).drop_duplicates()


def get_recommendations(track_name, num_recommendations=10):
    
    idx = music_indices[track_name][0]




    # Get similarity scores for the song
    sim_scores = list(enumerate(cos_similar[idx]))  # Get similarity scores for the song
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)  # Sort the songs by similarity

    sim_scores = sim_scores[1:num_recommendations + 1]

    sim_index = [i[0] for i in sim_scores]  # Get the indices of the recommended songs
    dataframe = songs_data.iloc[sim_index][['track_name', 'artist_name', 'lyrics', 'energy']]

    top_dataframe = dataframe.head(10)

    # Convert DataFrame to a list of dictionaries
    return top_dataframe[['track_name', 'artist_name', 'energy']].to_dict(orient='records')



