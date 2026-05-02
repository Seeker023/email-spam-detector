# 📧 Email Spam Detection System

A complete end-to-end Machine Learning pipeline to detect whether an email is **Spam** or **Ham** (Not Spam). 
This project uses NLP text processing and compares four classic ML models to find the best performing classifier.

## 📂 Project Structure

```
email_spam_detector/
├── data/              ← Directory for dataset (emails.csv)
├── plots/             ← Generated evaluation plots (Confusion matrices, ROC curve, etc.)
├── models/            ← Saved joblib files (best model & vectorizer)
├── src/
│   ├── download_data.py ← Script to fetch SpamAssassin public corpus
│   ├── preprocess.py    ← NLP text cleaning pipeline
│   ├── train.py         ← Model training, evaluation & plotting
│   └── predict.py       ← Inference logic for single email classification
├── app.py             ← Gradio Web UI
├── notebook.ipynb     ← Jupyter notebook with full EDA & Walkthrough
└── requirements.txt   ← Python dependencies
```

## 🚀 Setup & Installation

1. **Install Dependencies:**
   Make sure you have Python installed. Run the following command:
   ```bash
   pip install -r requirements.txt
   ```

2. **Download the Dataset:**
   If you don't have the Enron Kaggle dataset, run the provided script to automatically download and extract the Apache SpamAssassin public corpus:
   ```bash
   python src/download_data.py
   ```
   *This will create an `emails.csv` file in the `data/` directory.*

## 🧠 Training the Models

Run the training script to preprocess text, extract features (TF-IDF), and evaluate four models:
- Multinomial Naive Bayes
- Logistic Regression
- Linear SVM (SGDClassifier)
- Random Forest

```bash
python src/train.py
```

**What this script does:**
- Prints a comparison table of Accuracy, Precision, Recall, F1, and AUC-ROC.
- Saves Confusion Matrix heatmaps, a ROC-AUC curve, and a keyword importance bar chart in the `plots/` folder.
- Automatically saves the highest-performing model and the TF-IDF vectorizer to the `models/` directory.

## 🌐 Running the Web UI

To start the interactive web application, run:
```bash
python app.py
```
This will launch a Gradio interface locally. Open the provided URL in your browser, paste an email's text, and click "Analyze" to see if it is classified as Spam or Ham.
