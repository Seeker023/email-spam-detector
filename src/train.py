import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                             f1_score, roc_auc_score, confusion_matrix, roc_curve)

from src.preprocess import clean_text

def train_and_evaluate():
    base_dir = Path(__file__).parent.parent
    data_path = base_dir / "data" / "emails.csv"
    plots_dir = base_dir / "plots"
    models_dir = base_dir / "models"
    
    plots_dir.mkdir(exist_ok=True, parents=True)
    models_dir.mkdir(exist_ok=True, parents=True)
    
    if not data_path.exists():
        raise FileNotFoundError(f"Data file {data_path} not found. Please run src/download_data.py first.")
        
    print("Loading data...")
    df = pd.read_csv(data_path)
    df = df.dropna(subset=['text', 'spam'])
    
    print("Cleaning text (this may take a while)...")
    # Using a subset for faster execution if desired, but we process all here
    df['cleaned_text'] = df['text'].apply(clean_text)
    
    # Drop rows that became empty after cleaning
    df = df[df['cleaned_text'].str.strip() != ""]
    
    X = df['cleaned_text']
    y = df['spam'].astype(int)
    
    print("Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print("Vectorizing text...")
    vectorizer = TfidfVectorizer(max_features=10000, ngram_range=(1, 2))
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    # Define Models
    models = {
        "Naive Bayes": MultinomialNB(),
        "Logistic Regression": LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42),
        "Linear SVM": SGDClassifier(loss='log_loss', class_weight='balanced', random_state=42),
        "Random Forest": RandomForestClassifier(class_weight='balanced', n_estimators=100, n_jobs=-1, random_state=42)
    }
    
    results = []
    best_model = None
    best_f1 = 0
    best_model_name = ""
    
    plt.figure(figsize=(10, 8)) # For ROC Curve
    
    # Train & Evaluate
    for name, model in models.items():
        print(f"Training {name}...")
        model.fit(X_train_vec, y_train)
        
        y_pred = model.predict(X_test_vec)
        y_prob = model.predict_proba(X_test_vec)[:, 1] if hasattr(model, "predict_proba") else model.decision_function(X_test_vec)
        
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred)
        rec = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_prob)
        
        results.append({
            "Model": name,
            "Accuracy": acc,
            "Precision": prec,
            "Recall": rec,
            "F1": f1,
            "AUC-ROC": auc
        })
        
        if f1 > best_f1:
            best_f1 = f1
            best_model = model
            best_model_name = name
            
        # Plot ROC curve
        fpr, tpr, _ = roc_curve(y_test, y_prob)
        plt.plot(fpr, tpr, label=f"{name} (AUC = {auc:.3f})")
        
        # Plot Confusion Matrix
        cm = confusion_matrix(y_test, y_pred)
        plt.figure(figsize=(6, 4))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Ham', 'Spam'], yticklabels=['Ham', 'Spam'])
        plt.title(f'Confusion Matrix - {name}')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        plt.savefig(plots_dir / f'confusion_matrix_{name.replace(" ", "_").lower()}.png')
        plt.close()
        
    # Finalize ROC curve plot
    plt.figure(1) # Go back to ROC plot
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic (ROC) Comparison')
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(plots_dir / 'roc_auc_comparison.png')
    plt.close()
    
    # Print Comparison Table
    results_df = pd.DataFrame(results)
    print("\n--- Model Comparison ---")
    print(results_df.to_markdown(index=False))
    
    # Plot Model Accuracy Comparison
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Model', y='Accuracy', data=results_df, hue='Model', palette='viridis', legend=False)
    plt.title('Model Accuracy Comparison')
    plt.ylim(0.8, 1.0)
    plt.tight_layout()
    plt.savefig(plots_dir / 'accuracy_comparison.png')
    plt.close()
    
    # Plot Top 20 Spam vs Ham Keywords (Using Logistic Regression coefficients)
    lr_model = models["Logistic Regression"]
    feature_names = vectorizer.get_feature_names_out()
    coefs = lr_model.coef_[0]
    
    # Sort indices
    top_spam_idx = coefs.argsort()[-20:][::-1]
    top_ham_idx = coefs.argsort()[:20]
    
    top_spam_words = feature_names[top_spam_idx]
    top_spam_coefs = coefs[top_spam_idx]
    
    top_ham_words = feature_names[top_ham_idx]
    top_ham_coefs = coefs[top_ham_idx]
    
    plt.figure(figsize=(15, 10))
    
    plt.subplot(1, 2, 1)
    sns.barplot(x=top_spam_coefs, y=top_spam_words, hue=top_spam_words, palette='Reds_r', legend=False)
    plt.title('Top 20 Spam Keywords')
    plt.xlabel('Coefficient Value')
    
    plt.subplot(1, 2, 2)
    # Use absolute value for ham coefficients just for visualization magnitude
    sns.barplot(x=np.abs(top_ham_coefs), y=top_ham_words, hue=top_ham_words, palette='Blues_r', legend=False)
    plt.title('Top 20 Ham Keywords')
    plt.xlabel('Absolute Coefficient Value')
    
    plt.tight_layout()
    plt.savefig(plots_dir / 'top_keywords.png')
    plt.close()
    
    print(f"\nSaving Best Model ({best_model_name}) and Vectorizer to {models_dir}...")
    joblib.dump(best_model, models_dir / "best_model.joblib")
    joblib.dump(vectorizer, models_dir / "vectorizer.joblib")
    print("Done! Check the 'plots' folder for evaluation visuals.")

if __name__ == "__main__":
    train_and_evaluate()
