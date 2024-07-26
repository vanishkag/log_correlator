from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# MongoDB configuration
MONGO_URI = 'mongodb://localhost:27017'
DATABASE_NAME = 'log_db'
COLLECTION_NAME = 'logs'

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
logs_collection = db[COLLECTION_NAME]

@app.route('/api/logs', methods=['GET'])
def get_logs():
    logs = list(logs_collection.find())  # Fetch all logs from MongoDB
    for log in logs:
        log['_id'] = str(log['_id'])  # Convert ObjectId to string for JSON serialization
    return jsonify(logs)

@app.route('/api/logs', methods=['POST'])
def add_logs():
    new_logs = request.json
    logs_collection.insert_many(new_logs)
    return jsonify({'message': 'Logs added successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)
