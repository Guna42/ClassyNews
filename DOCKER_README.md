# Docker Setup for ClassiNews

## Quick Start

### Option 1: Simple Setup (Recommended)
Run everything with just the Flask backend serving the UI:

```bash
docker-compose up --build
```

Access the app at: **http://localhost:5000**

---

### Option 2: With Separate Frontend (Nginx Reverse Proxy)
If you want Nginx on port 80 and Flask on port 5000:

```bash
docker-compose -f docker-compose-with-frontend.yml up --build
```

Access the app at: **http://localhost**

---

## Files Structure

```
Dockerfile.backend       - Flask backend container
Dockerfile.frontend      - Optional Nginx reverse proxy
docker-compose.yml       - Single backend setup
docker-compose-with-frontend.yml - Backend + Nginx setup
frontend/nginx.conf      - Nginx configuration for proxying
requirements.txt         - Python dependencies
```

## Services

### Backend Service (ClassiNews Flask App)
- **Container Name:** `classinews-app`
- **Port:** `5000:5000`
- **Features:**
  - Flask web server with UI
  - ML model predictions
  - Prediction history tracking
  - JSON API endpoints

### Frontend Service (Optional Nginx Proxy)
- **Container Name:** `classinews-frontend`
- **Port:** `80:80`
- **Purpose:** Acts as reverse proxy to backend

## Volumes

The backend container mounts:
- `./prediction_history.json` - Persists prediction history
- `./templates/` - Flask HTML templates
- `./static/` - CSS and JavaScript files

## Environment Variables

Set in `docker-compose.yml`:
- `FLASK_ENV=production`
- `FLASK_APP=app.py`

## Stopping Containers

```bash
docker-compose down
```

To remove everything including volumes:

```bash
docker-compose down -v
```

## Viewing Logs

```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

## Rebuilding

To rebuild without cache:

```bash
docker-compose up --build --no-cache
```

---

## API Endpoints

### Web Interface
- `GET /` - Home page
- `GET /about` - About page
- `GET /history` - Prediction history
- `POST /predict` - Classify article (form submission)

### JSON API
- `POST /api/predict` - API endpoint for predictions

**Request:**
```json
{
  "article": "Your news article text here..."
}
```

**Response:**
```json
{
  "prediction": "category_name",
  "confidence": 0.95,
  "probabilities": {
    "category1": 0.95,
    "category2": 0.03,
    "category3": 0.02
  }
}
```

---

## Troubleshooting

### Port Already in Use
If port 5000 is already in use, modify `docker-compose.yml`:
```yaml
ports:
  - "8000:5000"  # Access at localhost:8000
```

### Models Not Found
Ensure these files are in the project root:
- `news_classifier.joblib`
- `tfidf_vectorizer.joblib`

### Permission Issues (Linux/Mac)
```bash
sudo docker-compose up --build
```

### Clear Docker Cache
```bash
docker system prune -a
docker-compose up --build --no-cache
```

---

**Status:** Ready to deploy! 🚀
