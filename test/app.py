#v1

from flask import Flask, jsonify, request
from pymongo import MongoClient
from flask_cors import CORS
from datetime import datetime, timedelta
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

@app.route('/logs/total', methods=['GET'])
def get_log_count():
    count = collection.count_documents({})
    return jsonify({'total': count})

@app.route('/logs/chart', methods=['GET'])
def get_logs_chart():
    date_str = request.args.get('date')
    if not date_str:
        return jsonify([]), 400

    try:
        # Parse the date string and create start and end datetime objects for the day
        date = datetime.strptime(date_str, '%Y-%m-%d')
        start_date = datetime(date.year, date.month, date.day, 0, 0, 0)
        end_date = start_date + timedelta(days=1)

        # MongoDB aggregation to count logs per minute
        pipeline = [
            {
                "$match": {
                    "timeGenerated": {
                        "$gte": start_date,
                        "$lt": end_date
                    }
                }
            },
            {
                "$group": {
                    "_id": {
                        "year": { "$year": "$timeGenerated" },
                        "month": { "$month": "$timeGenerated" },
                        "day": { "$dayOfMonth": "$timeGenerated" },
                        "hour": { "$hour": "$timeGenerated" },
                        "minute": { "$minute": "$timeGenerated" }
                    },
                    "count": { "$sum": 1 }
                }
            },
            {
                "$sort": { "_id": 1 }
            }
        ]

        results = list(collection.aggregate(pipeline))

        # Prepare the response data
        chart_data = []
        for result in results:
            time_str = f"{result['_id']['hour']:02d}:{result['_id']['minute']:02d}"
            chart_data.append({"minute": time_str, "count": result["count"]})

        return jsonify(chart_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Start the fetch.py script as a background process
    subprocess.Popen(["python", "fetch.py"])
    app.run(debug=True)
