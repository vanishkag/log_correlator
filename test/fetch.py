#v1

from datetime import datetime
import win32evtlog
import win32evtlogutil
import win32security
from pymongo import MongoClient
import time

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['event_logs']
collection = db['logs']

EVENTLOG_TYPE_NAMES = {
    0: 'Unknown',
    1: 'Error',
    2: 'Warning',
    4: 'Information',
    8: 'Audit Success',
    16: 'Audit Failure'
}

def fetch_logs():
    server = 'localhost'
    log_types = ['Application', 'Security', 'System']
    for log_type in log_types:
        hand = win32evtlog.OpenEventLog(server, log_type)
        flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
        events = win32evtlog.ReadEventLog(hand, flags, 0)
        for event in events:
            if not collection.find_one({"recordNumber": event.RecordNumber}):
                log = {
                    'recordNumber': event.RecordNumber,
                    'eventCategory': event.EventCategory,
                    'eventID': event.EventID,
                    'eventType': event.EventType,
                    'eventTypeName': EVENTLOG_TYPE_NAMES.get(event.EventType, 'Unknown'),
                    'timeGenerated': event.TimeGenerated,  # Store as datetime object
                    'sourceName': event.SourceName,
                    'message': win32evtlogutil.SafeFormatMessage(event, log_type),
                }
                collection.insert_one(log)

while True:
    fetch_logs()
    time.sleep(10)