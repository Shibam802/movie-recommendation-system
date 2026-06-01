# 🎬 CineMatch — AI Movie Recommendation System

> A full-stack, deployment-ready movie recommendation web app powered by Machine Learning — built for placement showcase.
<img width="1913" height="973" alt="image" src="https://github.com/user-attachments/assets/fe20f3fe-01a0-435d-9397-4b156dfa061e" />
<img width="1912" height="976" alt="image" src="https://github.com/user-attachments/assets/d42df891-7cec-44f6-80ac-3ae87319fccc" />
<img width="1909" height="976" alt="image" src="https://github.com/user-attachments/assets/59d942eb-44d7-4729-a208-fa3857b84352" />
<img width="1909" height="605" alt="image" src="https://github.com/user-attachments/assets/568d345f-f324-455e-9c59-95eb7894665a" />
<img width="1908" height="977" alt="image" src="https://github.com/user-attachments/assets/93b03409-90e7-4b08-b23a-e4c9e6c80b98" />

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0.3-black?style=flat-square&logo=flask)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.5.0-orange?style=flat-square&logo=scikit-learn)
![SQLite](https://img.shields.io/badge/SQLite-Database-blue?style=flat-square&logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## ✨ Features

- 🎥 **AI Movie Recommendations** — Content-based filtering using cosine similarity
- 🔍 **Smart Search** — Autocomplete with fuzzy matching
- ⭐ **Rating System** — Rate movies 1–5 stars
- 📈 **Trending Analytics** — Track most searched movies
- 🕒 **Search History** — View past recommendation sessions
- 🗄️ **SQLite Database** — Persistent storage for history & ratings
- 🌐 **RESTful API** — 7 clean endpoints
- 🎨 **Cinematic Dark UI** — Professional frontend with film aesthetics
- ☁️ **Cloud Ready** — Deployable on Railway, Render, Hugging Face

---

## 🖥️ Demo

> Search any movie → Get 6 AI-powered recommendations with real posters

```
http://localhost:5000
```

---

## 🗂️ Project Structure

```
movie-recommender/
├── backend/
│   └── app.py                  ← Flask REST API + ML model loader
├── frontend/
│   ├── templates/
│   │   └── index.html          ← Main HTML page
│   └── static/
│       ├── css/style.css       ← Cinematic dark theme
│       └── js/main.js          ← Frontend logic + OMDB poster API
├── data/
│   ├── movies.db               ← SQLite database (auto-created)
│   ├── tmdb_5000_movies.csv    ← TMDB dataset
│   └── tmdb_5000_credits.csv   ← TMDB credits dataset
├── models/
│   ├── movies_list.pkl         ← Trained movie dataframe
│   └── similarity.pkl          ← Cosine similarity matrix (4806×4806)
├── requirements.txt
├── Dockerfile
├── Procfile
├── start.sh                    ← Linux/Mac launcher
└── start.bat                   ← Windows launcher
```

---

## 🚀 Quick Start (Local)

### Step 1 — Clone the repository

```bash
git clone https://github.com/Shibam802/movie-recommendation-system.git
cd movie-recommendation-system
```

### Step 2 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 3 — Run the app

**Windows:**
```bash
.\start.bat
```

**Linux / macOS:**
```bash
chmod +x start.sh && ./start.sh
```

**Manual:**
```bash
cd backend
python app.py
```

### Step 4 — Open browser

```
http://localhost:5000
```

---

## 🧠 Machine Learning Pipeline

### Algorithm
**Content-Based Filtering**

### Features Used
| Feature | Description |
|---------|-------------|
| Overview | Movie plot summary |
| Genres | Movie categories |
| Cast | Top 3 cast members |
| Crew | Director name |
| Keywords | TMDB keywords |

### Pipeline Steps

```
Raw Data → Merge → Clean → Tokenize → Stem → Vectorize → Cosine Similarity
```

### Vectorization

```python
CountVectorizer(max_features=5000, stop_words='english')
```

### Similarity

```python
cosine_similarity(vectors)  # 4806 × 4806 matrix
```

---

## 🗃️ Database Schema

**SQLite** — `data/movies.db`

| Table | Columns | Purpose |
|-------|---------|---------|
| `search_history` | id, movie_title, recommendations, searched_at | Logs every search |
| `movie_ratings` | id, movie_title, rating, rated_at | Stores user ratings |
| `popular_searches` | id, movie_title, search_count, last_searched | Tracks trending movies |

---

## 🔌 REST API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/movies` | Get all 4806 movies |
| `POST` | `/api/recommend` | Get recommendations |
| `GET` | `/api/history` | Recent search history |
| `GET` | `/api/popular` | Most searched movies |
| `POST` | `/api/rate` | Submit a rating |
| `GET` | `/api/stats` | Dashboard statistics |
| `POST` | `/api/train` | Retrain the model |

### Example Request

```json
POST /api/recommend
{
  "movie": "Inception"
}
```

### Example Response

```json
{
  "movie": "Inception",
  "recommendations": [
    { "title": "Interstellar", "score": 94.2 },
    { "title": "The Prestige", "score": 91.5 },
    { "title": "Shutter Island", "score": 89.3 },
    { "title": "The Dark Knight", "score": 87.1 },
    { "title": "Memento", "score": 85.6 }
  ]
}
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Backend** | Python, Flask, Flask-CORS |
| **Database** | SQLite (sqlite3) |
| **ML Model** | Scikit-learn (CountVectorizer + Cosine Similarity) |
| **NLP** | NLTK (Porter Stemmer) |
| **Poster API** | OMDB API |
| **Server** | Gunicorn |
| **Deployment** | Railway / Render / Hugging Face |

---

## ☁️ Deployment

### Railway

1. Push to GitHub
2. Connect repo on [railway.app](https://railway.app)
3. Set start command:
```bash
cd backend && gunicorn app:app --bind 0.0.0.0:$PORT
```

### Render

1. Push to GitHub
2. New Web Service on [render.com](https://render.com)
3. Build command: `pip install -r requirements.txt`
4. Start command: `cd backend && gunicorn app:app --bind 0.0.0.0:$PORT`

### Hugging Face Spaces (Docker)

```bash
git push hf main
```

---

## 📊 Dataset

**TMDB 5000 Movies Dataset**
- 4806 movies after preprocessing
- Source: Kaggle TMDB 5000 Movie Dataset
- Features: title, genres, cast, crew, keywords, overview

---

## 🎯 Future Enhancements

- [ ] User Authentication & Profiles
- [ ] Collaborative Filtering
- [ ] Hybrid Recommendation System
- [ ] Watchlist Feature
- [ ] Real-Time Analytics Dashboard
- [ ] Recommendation Explanations

---

## 👨‍💻 Author

**Shibam Banik**

B.Tech Computer Science (Blockchain Technology)
Vellore Institute of Technology

[![GitHub](https://img.shields.io/badge/GitHub-Shibam802-black?style=flat-square&logo=github)](https://github.com/Shibam802)

---

## ⭐ Show Your Support

If you found this project useful, please give it a ⭐ on GitHub!

---

*Built for Placement Showcase — demonstrates ML, NLP, Flask, REST APIs, Database Management & Cloud Deployment*
