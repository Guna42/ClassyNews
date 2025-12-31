import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [article, setArticle] = useState('');
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handlePredict = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post('/api/predict', {
        article: article
      });
      setPrediction(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred');
      setPrediction(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <div className="container">
        <h1>📰 News Classifier</h1>
        <p className="subtitle">Classify news articles using AI</p>

        <form onSubmit={handlePredict} className="form">
          <textarea
            value={article}
            onChange={(e) => setArticle(e.target.value)}
            placeholder="Paste your news article here..."
            rows="8"
            required
          />
          <button type="submit" disabled={loading}>
            {loading ? 'Classifying...' : 'Classify Article'}
          </button>
        </form>

        {error && <div className="error">{error}</div>}

        {prediction && (
          <div className="results">
            <h2>Prediction Result</h2>
            <div className="prediction-box">
              <h3>{prediction.prediction}</h3>
              <p>Confidence: {(prediction.confidence * 100).toFixed(2)}%</p>
            </div>
            {prediction.probabilities && (
              <div className="probabilities">
                <h4>Category Probabilities:</h4>
                {Object.entries(prediction.probabilities).map(([cat, prob]) => (
                  <div key={cat} className="prob-item">
                    <span>{cat}</span>
                    <div className="progress-bar">
                      <div
                        className="progress-fill"
                        style={{ width: `${prob * 100}%` }}
                      />
                    </div>
                    <span>{(prob * 100).toFixed(2)}%</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
