import streamlit as st
import pandas as pd
import pickle
import requests
import time

API_KEY = "47e6a0a29373e751c0827d73c5727f52"
BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
TMDB_MOVIE_URL = "https://www.themoviedb.org/movie"


def get_poster_by_id(movie_id):
    """Fetch poster URL from TMDb API"""
    url = f"{BASE_URL}/movie/{movie_id}?api_key={API_KEY}"

    for _ in range(3):  # retry 3 times
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Return poster if present
            if data.get("poster_path"):
                return IMAGE_BASE_URL + data["poster_path"]

            return None

        except requests.exceptions.RequestException:
            time.sleep(2)

    return None


# Load data safely
try:
    with open('movies_dict.pkl', 'rb') as f:
        movies_dict = pickle.load(f)

    movies = pd.DataFrame(movies_dict)

    with open('similarity.pkl', 'rb') as f:
        similarity = pickle.load(f)

except Exception as e:
    st.error("❌ Error loading model files. Make sure your .pkl files exist.")
    st.stop()


def recommend(movie):
    """Recommend 5 similar movies"""
    try:
        movie_index = movies[movies['title'] == movie].index[0]
    except IndexError:
        return [], [], []

    distances = similarity[movie_index]
    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended_movies = []
    recommended_movies_img = []
    recommended_movies_id = []

    for i in movies_list:
        index = i[0]

        movie_id = movies.iloc[index]['id']
        title = movies.iloc[index]['title']

        recommended_movies.append(title)
        recommended_movies_img.append(get_poster_by_id(movie_id))
        recommended_movies_id.append(movie_id)

    return recommended_movies, recommended_movies_img, recommended_movies_id


# ---------------------- STREAMLIT UI ----------------------

st.title("🎬 Movie Recommender System")

selected_movie = st.selectbox(
    "What Movie Have You Watched?",
    movies['title'].values
)

if st.button("Recommend"):
    st.snow()

    names, posters, ids = recommend(selected_movie)

    if not names:
        st.error("❌ Could not find recommendations.")
    else:
        cols = st.columns(5)

        for idx, (name, poster, movie_id) in enumerate(zip(names, posters, ids)):
            col = cols[idx % 5]
            with col:
                if poster:
                    st.image(poster, use_container_width=True)
                else:
                    st.write("(no image)")

                st.caption(name)
                st.markdown(
                    f"[🔗 View Details]({TMDB_MOVIE_URL}/{movie_id})",
                    unsafe_allow_html=True
                )