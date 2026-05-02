import os
import nltk

# Ensure NLTK data directory exists and is writable
nltk_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nltk_data')
os.makedirs(nltk_data_dir, exist_ok=True)
nltk.data.path.append(nltk_data_dir)

# Download required NLTK data on app startup
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', download_dir=nltk_data_dir, quiet=True)
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet', download_dir=nltk_data_dir, quiet=True)
try:
    nltk.data.find('corpora/omw-1.4')
except LookupError:
    nltk.download('omw-1.4', download_dir=nltk_data_dir, quiet=True)

from flask import Flask, render_template, request, jsonify
from src.predict import predict_spam

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    email_text = data.get('text', '')
    
    if not email_text.strip():
        return jsonify({'error': 'No text provided'}), 400
        
    try:
        label, confidence = predict_spam(email_text)
        return jsonify({
            'label': label,
            'confidence': confidence,
            'status': 'success'
        })
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
