import joblib
import os
import math
from pathlib import Path
from src.preprocess import clean_text

# --- CACHE: Load model and vectorizer ONCE at module import ---
_base_dir = Path(__file__).parent.parent
_model_path = _base_dir / "models" / "best_model.joblib"
_vectorizer_path = _base_dir / "models" / "vectorizer.joblib"

if not _model_path.exists() or not _vectorizer_path.exists():
    raise FileNotFoundError("Model or Vectorizer not found. Please run train.py first.")

_model = joblib.load(_model_path)
_vectorizer = joblib.load(_vectorizer_path)
print(f"[SpamShield] Model and vectorizer loaded successfully from {_base_dir / 'models'}")


def predict_spam(text):
    """
    Predicts whether a given text is Spam or Ham.
    Returns:
        label (str): 'Spam' or 'Ham'
        confidence (float): Probability score percentage
    """
    # Preprocess
    cleaned_text = clean_text(text)
    if not cleaned_text.strip():
        return "Unknown", 0.0
        
    # Vectorize
    X_test = _vectorizer.transform([cleaned_text])
    
    # Predict
    prediction = _model.predict(X_test)[0]
    
    # Get probability if available
    try:
        prob = _model.predict_proba(X_test)[0]
        confidence = prob[prediction] * 100
    except AttributeError:
        # Linear SVM (SGDClassifier without log loss) might not have predict_proba
        # Alternatively, we can use decision_function
        try:
            decision = _model.decision_function(X_test)[0]
            # convert to pseudo-probability
            confidence = (1 / (1 + math.exp(-decision))) * 100
            if prediction == 0:
                confidence = 100 - confidence
        except:
            confidence = 100.0 # fallback
            
    label = "Spam" if prediction == 1 else "Ham"
    return label, round(confidence, 2)

if __name__ == "__main__":
    sample_text = "Congratulations! You've won a $1,000 Walmart gift card. Click here to claim your prize."
    label, conf = predict_spam(sample_text)
    print(f"Sample Text: {sample_text}")
    print(f"Prediction: {label} ({conf}%)")
