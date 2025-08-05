from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
import re

app = Flask(__name__)
app.secret_key = 'secretkey'

VOTES_FILE = 'votes.json'

CANDIDATES = ["Candidate A", "Candidate B", "Candidate C", "Candidate D", "Candidate E"]

# Initialize votes file if not present
if not os.path.exists(VOTES_FILE):
    with open(VOTES_FILE, 'w') as f:
        json.dump({"votes": {}, "voted_ids": []}, f)

def load_votes():
    with open(VOTES_FILE, 'r') as f:
        return json.load(f)

def save_votes(data):
    with open(VOTES_FILE, 'w') as f:
        json.dump(data, f)

@app.route('/')
def index():
    return render_template('index.html', candidates=CANDIDATES)

@app.route('/vote', methods=['POST'])
def vote():
    name = request.form.get('name')
    aadhar = request.form.get('aadhar')
    candidate = request.form.get('candidate')

    if not re.fullmatch(r'\d{12}', aadhar):
        return render_template('invalid_aadhar.html')

    data = load_votes()
    if aadhar in data['voted_ids']:
        return render_template('already_voted.html')

    # Count the vote
    data['votes'][candidate] = data['votes'].get(candidate, 0) + 1
    data['voted_ids'].append(aadhar)
    save_votes(data)

    return render_template('success.html', name=name)

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'password123':
            session['admin'] = True
            return redirect(url_for('results'))
        else:
            return render_template('admin_login.html', error="Invalid credentials")
    return render_template('admin_login.html')

@app.route('/results')
def results():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    data = load_votes()
    votes = data['votes']
    total_votes = sum(votes.values()) if votes else 0
    winner = max(votes, key=votes.get) if votes else "No votes yet"

    return render_template('results.html', votes=votes, winner=winner, total_votes=total_votes)

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)