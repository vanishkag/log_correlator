import time
import subprocess
import re
from datetime import datetime, timezone
import string
from pymongo import MongoClient

# MongoDB configuration
MONGO_URI = 'mongodb://localhost:27017'
DATABASE_NAME = 'log_db'
COLLECTION_NAME = 'logs'

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
logs_collection = db[COLLECTION_NAME]

SYSMON_LOG_NAME = 'Microsoft-Windows-Sysmon/Operational'  # Sysmon log name

last_fetch_time = None

def fetch_initial_logs():
    global last_fetch_time
    command = f'wevtutil qe {SYSMON_LOG_NAME} /c:20 /f:text /rd:true /q:"*"'
    result = subprocess.run(command, capture_output=True, text=True, shell=True)

    if result.returncode == 0:
        logs = parse_logs(result.stdout)
        if logs:
            save_logs_to_db(logs)
            # Update last_fetch_time to the timestamp of the last log in the initial fetch
            last_log_time = logs[-1].get('TimeCreated', None)
            if last_log_time:
                last_fetch_time = last_log_time
    else:
        print('Failed to fetch initial logs:', result.stderr)

def fetch_and_save_logs():
    global last_fetch_time
    fetch_initial_logs()

    while True:
        if last_fetch_time:
            # Adjust the query to fetch logs newer than the last_fetch_time
            command = f'wevtutil qe {SYSMON_LOG_NAME} /c:10 /f:text /rd:true /q:"*[System[TimeCreated[@SystemTime>{last_fetch_time}]]]"'
        else:
            # Fallback to fetching all logs if last_fetch_time is not set (shouldn't happen after initial fetch)
            command = f'wevtutil qe {SYSMON_LOG_NAME} /c:10 /f:text /rd:true /q:"*"'

        result = subprocess.run(command, capture_output=True, text=True, shell=True)

        if result.returncode == 0:
            logs = parse_logs(result.stdout)
            if logs:
                save_logs_to_db(logs)
                # Update last_fetch_time to the latest log entry's timestamp
                last_log_time = logs[-1].get('TimeCreated', None)
                if last_log_time:
                    last_fetch_time = last_log_time
        else:
            print('Failed to fetch logs:', result.stderr)

        time.sleep(2)  # Fetch logs every 2 seconds

def parse_logs(output):
    logs = []
    log_entries = output.strip().split('\r\n\r\n')
    for entry in log_entries:
        log = {}
        lines = entry.splitlines()
        for line in lines:
            line = remove_non_printable(line)  # Remove non-printable characters
            match = re.match(r'^\s*(\w+)\s*:\s*(.*)$', line)
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()  # Remove leading/trailing whitespace
                log[key] = value
        
        # Example filtering: Exclude logs with specific Description
        if 'Description' in log and 'Windows Event Log Utility' in log['Description']:
            continue  # Skip this log entry
        
        # Add only logs that are not filtered out
        logs.append(log)
    
    return logs

def remove_non_printable(text):
    printable = set(string.printable)
    return ''.join(filter(lambda x: x in printable, text))

def save_logs_to_db(logs):
    try:
        logs_collection.insert_many(logs)
        print('Logs saved to MongoDB successfully')
    except Exception as e:
        print(f'Error saving logs to MongoDB: {str(e)}')

if __name__ == '__main__':
    fetch_and_save_logs()
