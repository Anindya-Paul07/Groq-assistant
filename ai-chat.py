import os
import requests
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from werkzeug.utils import secure_filename
from zipfile import ZipFile
import tempfile

app = Flask(__name__)
app.secret_key = 'my2003' 
ACCESS_TOKEN = "supersecret123"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
UPLOAD_FOLDER = tempfile.gettempdir()

@app.route('/')
def index():
    if 'authenticated' not in session:
        return redirect(url_for('login'))
    return render_template('upload.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['password'] == 'admin123':
            session['authenticated'] = True
            return redirect(url_for('index'))
        return "Wrong password!"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('login'))

@app.route('/analyze', methods=['POST'])
def analyze():
    auth_header = request.headers.get('Authorization')
    if auth_header != f"Bearer {ACCESS_TOKEN}":
        return jsonify({'error': 'Unauthorized'}), 401

    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    prompt = f"Analyze the following code and suggest improvements:\n{content}"
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama3-8b-8192",
            "messages": [
                {"role": "system", "content": "You are a helpful AI code assistant."},
                {"role": "user", "content": prompt}
            ]
        }
    )
    return jsonify(response.json()['choices'][0]['message']['content'])

@app.route('/chat', methods=['POST'])
def chat():
    auth_header = request.headers.get('Authorization')
    if auth_header != f"Bearer {ACCESS_TOKEN}":
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    if not data or 'messages' not in data:
        return jsonify({'error': 'Invalid payload'}), 400

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama3-8b-8192",
            "messages": data['messages']
        }
    )
    return jsonify(response.json()['choices'][0]['message']['content'])

if __name__ == '__main__':
    app.run(debug=True)

