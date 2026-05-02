import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Ensure required NLTK resources are downloaded
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet', quiet=True)
    
try:
    nltk.data.find('corpora/omw-1.4')
except LookupError:
    nltk.download('omw-1.4', quiet=True)

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def clean_text(text):
    """
    Cleans email text by removing HTML tags, URLs, punctuation,
    lowercasing, removing stopwords, and applying lemmatization.
    """
    if not isinstance(text, str):
        return ""
        
    # 1. Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    
    # 2. Remove URLs
    text = re.sub(r'(http|https)://[^\s]*', 'httpaddr', text)
    
    # 3. Remove Email Addresses
    text = re.sub(r'[^\s]+@[^\s]+', 'emailaddr', text)
    
    # 4. Remove Numbers
    text = re.sub(r'[0-9]+', 'number', text)
    
    # 5. Remove currency symbols (optional but helpful for spam)
    text = re.sub(r'[$£€]', 'currency', text)
    
    # 6. Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # 7. Lowercase
    text = text.lower()
    
    # 8. Tokenize (split by whitespace), remove stopwords, and lemmatize
    words = text.split()
    cleaned_words = [lemmatizer.lemmatize(word) for word in words if word not in stop_words]
    
    return " ".join(cleaned_words)
