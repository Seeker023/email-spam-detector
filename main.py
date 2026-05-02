from flask import Flask, render_template, request, jsonify
import os
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
