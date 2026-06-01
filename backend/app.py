from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import pickle
import sqlite3
import os
import json
from datetime import datetime

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
CORS(app)

DB_PATH = os.path.join(os.path.dirname(__file__), '../data/movies.db')
MODEL_PATH = os.path.join(os.path.dirname(__file__), '../models/')

# ─── Database Setup ───────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_title TEXT NOT NULL,
            recommendations TEXT NOT NULL,
            searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS movie_ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_title TEXT NOT NULL,
            rating INTEGER CHECK(rating BETWEEN 1 AND 5),
            rated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS popular_searches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_title TEXT UNIQUE NOT NULL,
            search_count INTEGER DEFAULT 1,
            last_searched TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# ─── Load ML Model ────────────────────────────────────────────────────────────

new_df = None
similarity = None

def load_model():
    global new_df, similarity
    try:
        import pandas as pd
        import pickle
        new_df = pickle.load(open(os.path.join(MODEL_PATH, 'movies_list.pkl'), 'rb'))
        similarity = pickle.load(open(os.path.join(MODEL_PATH, 'similarity.pkl'), 'rb'))
        print(f"✅ Model loaded: {len(new_df)} movies")
        return True
    except Exception as e:
        print(f"⚠️  Model not found, using demo mode: {e}")
        return False

def get_demo_movies():
    return [
        "The Dark Knight", "Inception", "Interstellar", "The Matrix",
        "Pulp Fiction", "Goodfellas", "Fight Club", "Forrest Gump",
        "The Shawshank Redemption", "The Godfather", "Avatar",
        "The Avengers", "Iron Man", "Batman Begins", "Spider-Man",
        "Jurassic Park", "Titanic", "Star Wars", "The Lion King",
        "Schindler's List", "Saving Private Ryan", "Gladiator",
        "The Silence of the Lambs", "Toy Story", "Finding Nemo",
        "Pirates of the Caribbean", "Harry Potter", "Lord of the Rings",
        "The Hobbit", "Mad Max: Fury Road", "Gravity", "The Martian"
    ]

demo_recommendations = {
    "The Dark Knight": ["Batman Begins", "The Dark Knight Rises", "Batman v Superman", "Man of Steel", "Watchmen"],
    "Inception": ["Interstellar", "The Matrix", "Shutter Island", "Memento", "Tenet"],
    "Interstellar": ["Inception", "Gravity", "The Martian", "2001: A Space Odyssey", "Contact"],
    "default": ["The Dark Knight", "Inception", "Interstellar", "Pulp Fiction", "Fight Club"]
}

# ─── API Routes ───────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/movies', methods=['GET'])
def get_movies():
    """Return list of all available movies"""
    if new_df is not None:
        movies = new_df['title'].tolist()
    else:
        movies = get_demo_movies()
    return jsonify({'movies': movies, 'count': len(movies)})

@app.route('/api/recommend', methods=['POST'])
def recommend():
    """Get recommendations for a movie"""
    data = request.get_json()
    movie_title = data.get('movie', '').strip()

    if not movie_title:
        return jsonify({'error': 'Movie title is required'}), 400

    recommendations = []

    if new_df is not None and similarity is not None:
        matches = new_df[new_df['title'].str.lower() == movie_title.lower()]
        if matches.empty:
            # fuzzy match
            matches = new_df[new_df['title'].str.lower().str.contains(movie_title.lower())]
        if matches.empty:
            return jsonify({'error': f'Movie "{movie_title}" not found in database'}), 404

        movie_index = matches.index[0]
        actual_title = new_df.iloc[movie_index]['title']
        distances = similarity[movie_index]
        import numpy as np
        movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:11]
        recommendations = [
            {'title': new_df.iloc[i[0]]['title'], 'score': round(float(i[1]) * 100, 1)}
            for i in movies_list
        ]
    else:
        # Demo mode
        actual_title = movie_title
        rec_titles = demo_recommendations.get(movie_title, demo_recommendations['default'])
        recommendations = [{'title': t, 'score': round(95 - idx * 5, 1)} for idx, t in enumerate(rec_titles)]

    # Save to DB
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute(
            'INSERT INTO search_history (movie_title, recommendations) VALUES (?, ?)',
            (actual_title, json.dumps([r['title'] for r in recommendations]))
        )
        c.execute('''
            INSERT INTO popular_searches (movie_title, search_count, last_searched)
            VALUES (?, 1, CURRENT_TIMESTAMP)
            ON CONFLICT(movie_title) DO UPDATE SET
                search_count = search_count + 1,
                last_searched = CURRENT_TIMESTAMP
        ''', (actual_title,))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"DB error: {e}")

    return jsonify({
        'movie': actual_title,
        'recommendations': recommendations[:6],
        'total': len(recommendations)
    })

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get recent search history"""
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT * FROM search_history ORDER BY searched_at DESC LIMIT 20')
        rows = c.fetchall()
        conn.close()
        history = [
            {
                'id': r['id'],
                'movie': r['movie_title'],
                'recommendations': json.loads(r['recommendations']),
                'searched_at': r['searched_at']
            } for r in rows
        ]
        return jsonify({'history': history})
    except Exception as e:
        return jsonify({'history': [], 'error': str(e)})

@app.route('/api/popular', methods=['GET'])
def get_popular():
    """Get most searched movies"""
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT movie_title, search_count FROM popular_searches ORDER BY search_count DESC LIMIT 10')
        rows = c.fetchall()
        conn.close()
        return jsonify({'popular': [{'title': r['movie_title'], 'count': r['search_count']} for r in rows]})
    except Exception as e:
        return jsonify({'popular': [], 'error': str(e)})

@app.route('/api/rate', methods=['POST'])
def rate_movie():
    """Save a movie rating"""
    data = request.get_json()
    movie = data.get('movie', '').strip()
    rating = data.get('rating')
    if not movie or not rating:
        return jsonify({'error': 'Movie and rating required'}), 400
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('INSERT INTO movie_ratings (movie_title, rating) VALUES (?, ?)', (movie, rating))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': f'Rated "{movie}" {rating}/5'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get overall stats"""
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT COUNT(*) as total FROM search_history')
        total_searches = c.fetchone()['total']
        c.execute('SELECT COUNT(DISTINCT movie_title) as unique_movies FROM search_history')
        unique_movies = c.fetchone()['unique_movies']
        c.execute('SELECT AVG(rating) as avg_rating FROM movie_ratings')
        avg_rating = c.fetchone()['avg_rating']
        conn.close()
        return jsonify({
            'total_searches': total_searches,
            'unique_movies': unique_movies,
            'avg_rating': round(avg_rating or 0, 1),
            'total_movies': len(new_df) if new_df is not None else len(get_demo_movies())
        })
    except Exception as e:
        return jsonify({'total_searches': 0, 'unique_movies': 0, 'avg_rating': 0, 'total_movies': 0})

# ─── Model Training Route ─────────────────────────────────────────────────────

@app.route('/api/train', methods=['POST'])
def train_model():
    """Train model from uploaded CSV files"""
    import os
    movies_csv = os.path.join(os.path.dirname(__file__), '../data/tmdb_5000_movies.csv')
    credits_csv = os.path.join(os.path.dirname(__file__), '../data/tmdb_5000_credits.csv')

    if not os.path.exists(movies_csv) or not os.path.exists(credits_csv):
        return jsonify({'error': 'CSV files not found. Place tmdb_5000_movies.csv and tmdb_5000_credits.csv in data/ folder'}), 400

    try:
        import pandas as pd
        import numpy as np
        import ast
        import pickle
        import nltk
        from nltk.stem.porter import PorterStemmer
        from sklearn.feature_extraction.text import CountVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        nltk.download('punkt', quiet=True)

        movies = pd.read_csv(movies_csv)
        credits = pd.read_csv(credits_csv)
        movies = movies.merge(credits, on='title')
        movies = movies[['movie_id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew']]
        movies.dropna(inplace=True)

        def convert(obj):
            return [i['name'] for i in ast.literal_eval(obj)]

        def convert3(obj):
            return [i['name'] for idx, i in enumerate(ast.literal_eval(obj)) if idx < 3]

        def fetch_director(obj):
            return [i['name'] for i in ast.literal_eval(obj) if i['job'] == 'Director'][:1]

        movies['genres'] = movies['genres'].apply(convert)
        movies['keywords'] = movies['keywords'].apply(convert)
        movies['cast'] = movies['cast'].apply(convert3)
        movies['crew'] = movies['crew'].apply(fetch_director)
        movies['overview'] = movies['overview'].apply(lambda x: x.split())
        for col in ['genres', 'keywords', 'cast', 'crew']:
            movies[col] = movies[col].apply(lambda x: [i.replace(" ", "") for i in x])

        movies['tags'] = movies['overview'] + movies['genres'] + movies['cast'] + movies['crew']
        new_df = movies[['movie_id', 'title', 'tags']].copy()
        new_df['tags'] = new_df['tags'].apply(lambda x: " ".join(x).lower())

        ps = PorterStemmer()
        new_df['tags'] = new_df['tags'].apply(lambda text: " ".join([ps.stem(w) for w in text.split()]))

        cv = CountVectorizer(max_features=5000, stop_words='english')
        vectors = cv.fit_transform(new_df['tags'])
        similarity = cosine_similarity(vectors)

        os.makedirs(MODEL_PATH, exist_ok=True)
        pickle.dump(new_df, open(os.path.join(MODEL_PATH, 'movies_list.pkl'), 'wb'))
        pickle.dump(similarity, open(os.path.join(MODEL_PATH, 'similarity.pkl'), 'wb'))

        load_model()
        return jsonify({'success': True, 'message': f'Model trained on {len(new_df)} movies!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    load_model()
    app.run(debug=True, port=5000)
