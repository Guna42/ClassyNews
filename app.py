from flask import Flask, render_template, request, jsonify, session
import joblib
import re
import nltk
from nltk.corpus import stopwords
from datetime import datetime
import json
import os

# Download stopwords if not present
nltk.download("stopwords", quiet=True)

STOP = set(stopwords.words("english"))

# ----------------------------
# CLEANING FUNCTION (EXACT COPY FROM NOTEBOOK)
# ----------------------------
def clean_text(text):
    text = text.lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    tokens = text.split()
    tokens = [t for t in tokens if t not in STOP]
    return " ".join(tokens)

# ----------------------------
# LOAD MODEL + TFIDF
# ----------------------------
tfidf = joblib.load("tfidf_vectorizer.joblib")
model = joblib.load("news_classifier.joblib")

# ----------------------------
# SETUP FLASK APP
# ----------------------------
app = Flask(__name__, 
            template_folder='templates', 
            static_folder='static',
            static_url_path='/static')
app.secret_key = os.urandom(24)  # For session management

# History storage (in production, use a database)
HISTORY_FILE = "prediction_history.json"

def load_history():
    """Load prediction history from file"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_history(entry):
    """Save prediction to history"""
    history = load_history()
    history.insert(0, entry)  # Add to beginning
    # Keep only last 100 predictions
    history = history[:100]
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
    except:
        pass

@app.route("/")
def home():
    return render_template("home.html", current_year=datetime.now().year)

@app.route("/about")
def about():
    return render_template("about.html", current_year=datetime.now().year)

@app.route("/history")
def history():
    history_data = load_history()
    # Calculate statistics
    stats = {
        'total': len(history_data),
        'categories': {}
    }
    for entry in history_data:
        cat = entry.get('prediction', 'Unknown')
        stats['categories'][cat] = stats['categories'].get(cat, 0) + 1
    
    return render_template("history.html", 
                         history=history_data[:20],  # Show last 20
                         stats=stats,
                         current_year=datetime.now().year)

@app.route("/api-docs")
def api_docs():
    return render_template("api_docs.html", current_year=datetime.now().year)

@app.route("/predict", methods=["POST"])
def predict():
    article = request.form.get("article", "")

    if not article:
        return render_template(
            "home.html",
            error="Please provide an article to classify.",
            current_year=datetime.now().year
        )

    # 1. Clean text EXACTLY like training
    cleaned = clean_text(article)

    # 2. Convert to TF-IDF using SAME vectorizer
    vector = tfidf.transform([cleaned])

    # 3. Predict category
    prediction = model.predict(vector)[0]

    # Save to history
    entry = {
        'article': article[:200] + "..." if len(article) > 200 else article,
        'prediction': prediction,
        'timestamp': datetime.now().isoformat()
    }
    save_history(entry)

    return render_template(
        "home.html",
        prediction_text="Predicted Category: " + prediction,
        article_text=article,
        current_year=datetime.now().year
    )

@app.route("/api/predict", methods=["POST"])
def api_predict():
    """API endpoint for predictions"""
    try:
        data = request.get_json()
        article = data.get("article", "")

        if not article:
            return jsonify({"error": "Article text is required"}), 400

        # Clean and predict
        cleaned = clean_text(article)
        vector = tfidf.transform([cleaned])
        prediction = model.predict(vector)[0]

        # Get prediction probabilities
        probabilities = model.predict_proba(vector)[0]
        classes = model.classes_
        confidence = max(probabilities)

        # Save to history
        entry = {
            'article': article[:200] + "..." if len(article) > 200 else article,
            'prediction': prediction,
            'timestamp': datetime.now().isoformat()
        }
        save_history(entry)

        return jsonify({
            "prediction": prediction,
            "confidence": float(confidence),
            "probabilities": {str(classes[i]): float(probabilities[i]) for i in range(len(classes))}
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Run on 0.0.0.0 for Docker and production
    host = "0.0.0.0"
    debug = False
    app.run(host=host, port=5000, debug=debug)
