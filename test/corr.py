from pymongo import MongoClient
from datetime import datetime, timedelta

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['event_logs']
collection = db['logs']

def fetch_logs():
    # Fetch all logs from MongoDB
    logs = list(collection.find().sort('timeGenerated', 1))
    return logs

def correlate_events(logs):
    correlated_events = []
    
    for i, event in enumerate(logs):
        # Failed Logon followed by Successful Logon
        if event['eventID'] == 4625:
            for j in range(i+1, len(logs)):
                if logs[j]['eventID'] == 4624 and logs[j].get('user') == event.get('user') and \
                   (logs[j]['timeGenerated'] - event['timeGenerated']).total_seconds() <= 300:
                    correlated_events.append((event, logs[j]))
                    break
        
        # Failed Logon followed by Account Lockout
        if event['eventID'] == 4625:
            for j in range(i+1, len(logs)):
                if logs[j]['eventID'] == 4740 and logs[j].get('user') == event.get('user') and \
                   (logs[j]['timeGenerated'] - event['timeGenerated']).total_seconds() <= 300:
                    correlated_events.append((event, logs[j]))
                    break
        
        # Process Creation followed by Termination
        if event['eventID'] == 4688:
            for j in range(i+1, len(logs)):
                if logs[j]['eventID'] == 4689 and logs[j].get('process_id') == event.get('process_id') and \
                   (logs[j]['timeGenerated'] - event['timeGenerated']).total_seconds() <= 600:
                    correlated_events.append((event, logs[j]))
                    break
        
        # Service Start followed by Service Stop
        if event['eventID'] == 7045:
            for j in range(i+1, len(logs)):
                if logs[j]['eventID'] == 7036 and logs[j].get('service_name') == event.get('service_name') and \
                   (logs[j]['timeGenerated'] - event['timeGenerated']).total_seconds() <= 1800:
                    correlated_events.append((event, logs[j]))
                    break
        
        # Privilege Use followed by Process Creation
        if event['eventID'] == 4672:
            for j in range(i+1, len(logs)):
                if logs[j]['eventID'] == 4688 and logs[j].get('user') == event.get('user') and \
                   (logs[j]['timeGenerated'] - event['timeGenerated']).total_seconds() <= 600:
                    correlated_events.append((event, logs[j]))
                    break
        
        # File Access followed by File Modification
        if event['eventID'] == 4663:
            for j in range(i+1, len(logs)):
                if logs[j]['eventID'] == 4660 and logs[j].get('file') == event.get('file') and \
                   (logs[j]['timeGenerated'] - event['timeGenerated']).total_seconds() <= 300:
                    correlated_events.append((event, logs[j]))
                    break
    
    return correlated_events

if __name__ == "__main__":
    logs = fetch_logs()
    correlated_events = correlate_events(logs)
    for event_pair in correlated_events:
        print("Correlated Events:")
        print(f"Event 1: {event_pair[0]}")
        print(f"Event 2: {event_pair[1]}")
