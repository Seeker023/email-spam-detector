import os
import tarfile
import requests
import pandas as pd
from pathlib import Path
import email

def download_file(url, target_path):
    print(f"Downloading {url}...")
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(target_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("Download complete.")
    else:
        print(f"Failed to download. Status code: {response.status_code}")

def extract_tarball(tar_path, extract_path):
    print(f"Extracting {tar_path}...")
    with tarfile.open(tar_path, "r:bz2") as tar:
        tar.extractall(path=extract_path)

def extract_email_body(filepath):
    try:
        with open(filepath, 'r', encoding='latin1') as f:
            msg = email.message_from_file(f)
            
        # Extract body
        body = []
        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                if ctype in ('text/plain', 'text/html'):
                    try:
                        body.append(part.get_payload(decode=True).decode('latin1', errors='ignore'))
                    except:
                        pass
        else:
            body.append(msg.get_payload(decode=True).decode('latin1', errors='ignore'))
            
        return "\n".join(body).strip()
    except Exception as e:
        return ""

def main():
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / "data"
    data_dir.mkdir(exist_ok=True, parents=True)
    
    ham_url = "https://spamassassin.apache.org/old/publiccorpus/20030228_easy_ham.tar.bz2"
    spam_url = "https://spamassassin.apache.org/old/publiccorpus/20030228_spam.tar.bz2"
    
    ham_tar = data_dir / "easy_ham.tar.bz2"
    spam_tar = data_dir / "spam.tar.bz2"
    
    if not ham_tar.exists():
        download_file(ham_url, ham_tar)
    if not spam_tar.exists():
        download_file(spam_url, spam_tar)
        
    extract_tarball(ham_tar, data_dir)
    extract_tarball(spam_tar, data_dir)
    
    ham_dir = data_dir / "easy_ham"
    spam_dir = data_dir / "spam"
    
    emails_data = []
    
    # Read Ham
    print("Reading Ham emails...")
    for filename in os.listdir(ham_dir):
        if filename != "cmds":
            filepath = ham_dir / filename
            body = extract_email_body(filepath)
            if body:
                emails_data.append({"text": body, "spam": 0})
                
    # Read Spam
    print("Reading Spam emails...")
    for filename in os.listdir(spam_dir):
        if filename != "cmds":
            filepath = spam_dir / filename
            body = extract_email_body(filepath)
            if body:
                emails_data.append({"text": body, "spam": 1})
                
    df = pd.DataFrame(emails_data)
    
    # Some emails might be empty after extraction
    df = df.dropna().drop_duplicates()
    df = df[df['text'].str.len() > 10]
    
    csv_path = data_dir / "emails.csv"
    df.to_csv(csv_path, index=False)
    print(f"Dataset successfully saved to {csv_path} with {len(df)} records.")

if __name__ == "__main__":
    main()
