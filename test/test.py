from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['event_logs']
collection = db['logs']

pipeline = [
    {
        "$group": {
            "_id": "$eventID"
        }
    },
    {
        "$project": {
            "_id": 0,
            "eventID": "$_id"
        }
    }
]

results = list(collection.aggregate(pipeline))

for result in results:
    print(result['eventID'])
