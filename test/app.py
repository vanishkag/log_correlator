from flask import Flask, jsonify, request
from pymongo import MongoClient
from flask_cors import CORS
import subprocess

app = Flask(__name__)
CORS(app)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['event_logs']
collection = db['logs']

@app.route('/logs', methods=['GET'])
def get_logs():
    query = {}
    if 'search' in request.args:
        search = request.args.get('search')
        query = {'message': {'$regex': search, '$options': 'i'}}

    # Sort logs by timeGenerated in descending order
    logs = list(collection.find(query).sort('timeGenerated', -1))
    for log in logs:
        log['_id'] = str(log['_id'])
    return jsonify(logs)

# Endpoint to get the total number of logs
@app.route('/logs/total', methods=['GET'])
def get_log_count():
    count = collection.count_documents({})
    return jsonify({'total': count})

if __name__ == '__main__':
    # Start the fetch.py script as a background process
    subprocess.Popen(["python", "fetch.py"])
    app.run(debug=True)
