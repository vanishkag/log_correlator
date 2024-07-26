import time
import subprocess
import requests
import re
from datetime import datetime

API_URL = 'http://localhost:5000/api/logs'  # Replace with your Flask API URL
CBS_LOG_NAME = 'Microsoft-Windows-Diagnostics-Performance/Operational'  # CBS log name
FETCH_INITIAL_COUNT = 20  # Number of logs to fetch initially

last_fetch_time = None

def fetch_and_send_logs():
    global last_fetch_time
    initial_fetch = True
    
    while True:
        if initial_fetch:
            command = f'wevtutil qe {CBS_LOG_NAME} /c:{FETCH_INITIAL_COUNT} /f:text /rd:true /q:"*"'
            initial_fetch = False
        else:
            if last_fetch_time is None:
                command = f'wevtutil qe {CBS_LOG_NAME} /c:10 /f:text /rd:true /q:"*"'
            else:
                command = f'wevtutil qe {CBS_LOG_NAME} /c:10 /f:text /rd:true /q:"*[System[TimeCreated[@SystemTime>\'{last_fetch_time}\']]]"'
        
        result = subprocess.run(command, capture_output=True, text=True, shell=True)

        if result.returncode == 0:
            logs = parse_logs(result.stdout)
            if logs:
                if initial_fetch:
                    # Skip sending logs during initial fetch
                    print(f'Initial {FETCH_INITIAL_COUNT} logs fetched.')
                else:
                    send_logs_to_api(logs)
                last_fetch_time = datetime.utcnow().isoformat() + 'Z'  # Update last fetch time to current UTC time
        else:
            print('Failed to fetch logs:', result.stderr)

        time.sleep(10)  # Fetch logs every 10 seconds

def parse_logs(output):
    logs = []
    log_entries = output.strip().split('\r\n\r\n')
    for entry in log_entries:
        log = {}
        lines = entry.splitlines()
        for line in lines:
            match = re.match(r'\s*(\w+)\s*:\s*(.*)', line)
            if match:
                key = match.group(1)
                value = match.group(2)
                log[key] = value
        logs.append(log)
    return logs

def send_logs_to_api(logs):
    try:
        response = requests.post(API_URL, json=logs)
        if response.status_code == 200:
            for log in logs:
                print(f'Log sent successfully: {log}')
        else:
            print(f'Failed to send logs: {response.status_code}')
    except requests.RequestException as e:
        print(f'Error sending logs: {str(e)}')

if __name__ == '__main__':
    fetch_and_send_logs()
