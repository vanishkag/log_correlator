import re
import json

path = r"C:\Users\nanda\Documents\intel\log_correlator\Windows_2k.log"

# Define the EventId and EventTemplate mappings with messages
event_patterns = {
    'E1': (r'^(\d+),(\d{4}-\d{2}-\d{2}),(\d{2}:\d{2}:\d{2}),(\w+),(\w+),\"00000006 Created NT transaction \(seq (\d+)\) result (0x[0-9a-fA-F]+), handle @(.+?)\"$', '<*> Created NT transaction (seq <*>) result <*>, handle @<*>'),
    'E2': (r'^(\d+),(\d{4}-\d{2}-\d{2}),(\d{2}:\d{2}:\d{2}),(\w+),(\w+), objectname \[<(.+?)>\]\"\(null\)\"$', 'Creating NT transaction (seq <*>), objectname [<*>]"(null)"'),
    'E3': (r'^<(.+?)> CSI perf trace:$', 'CSI perf trace:'),
    'E4': (r'^<(.+?)> CSI Store (.+?) \((.+?)\) initialized$', 'CSI Store <*> (<*>) initialized'),
    'E5': (r'^(\d+),(\d{4}-\d{2}-\d{2}),(\d{2}:\d{2}:\d{2}),(\w+),(\w+),\"00000004 IAdvancedInstallerAwareStore_ResolvePendingTransactions \(call (.+?)\) \(flags = (.+?), progress = (.+?), phase = (.+?), pdwDisposition = @(.+?)\"$', 'IAdvancedInstallerAwareStore_ResolvePendingTransactions (call <*>) (flags = <*>, progress = <*>, phase = <*>, pdwDisposition = @<*>)'),
    'E6': (r'^<(.+?)> ICSITransaction::Commit calling IStorePendingTransaction::Apply - coldpatching=FALSE applyflags=<(.+?)>$', 'ICSITransaction::Commit calling IStorePendingTransaction::Apply - coldpatching=FALSE applyflags=<*>'),
    'E7': (r'^<(.+?)> Performing (.+?) operations; (.+?) are not lock/unlock and follow:$', 'Performing <*> operations; <*> are not lock/unlock and follow:'),
    'E8': (r'^<(.+?)> Store coherency cookie matches last scavenge cookie, skipping scavenge\.$', 'Store coherency cookie matches last scavenge cookie, skipping scavenge.'),
    'E9': (r'^<(.+?)>@<(.+?)/(.+?)/(.+?):(.+?):(.+?):\.(.+?) CSI Transaction @<(.+?)> destroyed$', '@<*>/<*>/<*>:<*>:<*>:<*>.<*> CSI Transaction @<*> destroyed'),
    'E10': (r'^<(.+?)>@<(.+?)/(.+?)/(.+?):(.+?):(.+?):\.(.+?) CSI Transaction @<(.+?)> initialized for deployment engine \{(.+?)\} with flags (.+?) and client id \[<(.+?)>\]\"<(.+?)>/\"$', '@<*>/<*>/<*>:<*>:<*>:<*>.<*> CSI Transaction @<*> initialized for deployment engine {<*>} with flags <*> and client id [<*>]"<*>/"'),
    'E11': (r'^<(.+?)>@<(.+?)/(.+?)/(.+?):(.+?):(.+?):\.(.+?) PopulateComponentFamiliesKey - Begin$', '@<*>/<*>/<*>:<*>:<*>:<*>.<*> PopulateComponentFamiliesKey - Begin'),
    'E12': (r'^<(.+?)>@<(.+?)/(.+?)/(.+?):(.+?):(.+?):\.(.+?) PopulateComponentFamiliesKey - End$', '@<*>/<*>/<*>:<*>:<*>:<*>.<*> PopulateComponentFamiliesKey - End'),
    'E13': (r'^(\d+)@(\d{4}/\d{1,2}/\d{1,2}:\d{2}:\d{2}:\d{2}\.\d{3}) (\w+) \(wcp\.dll version ([\d\.]+)\) called \(stack (.+)\)$', '@<*>@<*>/<*>/<*>:<*>:<*>:<*>.<*> WcpInitialize (wcp.dll version <*>) called (stack @<*>'),
    'E14': (r'^Disabling manifest caching, because the image is not writeable\.$', 'Disabling manifest caching, because the image is not writeable.'),
    'E15': (r'^Ending the TrustedInstaller main loop\.$', 'Ending the TrustedInstaller main loop.'),
    'E16': (r'^Ending TrustedInstaller finalization\.$', 'Ending TrustedInstaller finalization.'),
    'E17': (r'^Ending TrustedInstaller initialization\.$', 'Ending TrustedInstaller initialization.'),
    'E18': (r'^Expecting attribute name \[HRESULT = (.+?) - CBS_E_MANIFEST_INVALID_ITEM\]$', 'Expecting attribute name [HRESULT = <*> - CBS_E_MANIFEST_INVALID_ITEM]'),
    'E19': (r'^Failed to create backup log cab\. \[HRESULT = (.+?) - ERROR_INVALID_FUNCTION\]$', 'Failed to create backup log cab. [HRESULT = <*> - ERROR_INVALID_FUNCTION]'),
    'E20': (r'^Failed to get next element \[HRESULT = (.+?) - CBS_E_MANIFEST_INVALID_ITEM\]$', 'Failed to get next element [HRESULT = <*> - CBS_E_MANIFEST_INVALID_ITEM]'),
    'E21': (r'^Failed to internally open package\. \[HRESULT = (.+?) - CBS_E_INVALID_PACKAGE\]$', 'Failed to internally open package. [HRESULT = <*> - CBS_E_INVALID_PACKAGE]'),
    'E22': (r'^Idle processing thread terminated normally$', 'Idle processing thread terminated normally'),
    'E23': (r'^Loaded Servicing Stack (.+?) with Core: (.+?)\\cbscore\.dll$', 'Loaded Servicing Stack <*> with Core: <*>\cbscore.dll'),
    'E24': (r'^Loading offline registry hive: (.+?), into registry key \'(.+?)\' from path \'(.+?)\'\.$', 'Loading offline registry hive: <*>, into registry key \'<*>\' from path \'<*>\'.'),
    'E25': (r'^No startup processing required, TrustedInstaller service was not set as autostart, or else a reboot is still pending\.$', 'No startup processing required, TrustedInstaller service was not set as autostart, or else a reboot is still pending.'),
    'E26': (r'^NonStart: Checking to ensure startup processing was not required\.$', 'NonStart: Checking to ensure startup processing was not required.'),
    'E27': (r'^NonStart: Success, startup processing not required as expected\.$', 'NonStart: Success, startup processing not required as expected.'),
    'E28': (r'^Offline image is: read-only$', 'Offline image is: read-only'),
    'E29': (r'^Read out cached package applicability for package: (.+?), ApplicableState: (.+?), CurrentState:(.+?)$', 'Read out cached package applicability for package: <*>, ApplicableState: <*>, CurrentState:<*>'),
    'E30': (r'^Reboot mark refs incremented to: (.+?)$', 'Reboot mark refs incremented to: <*>'),
    'E31': (r'^Reboot mark refs: (.+?)$', 'Reboot mark refs: <*>'),
    'E32': (r'^Scavenge: Begin CSI Store$', 'Scavenge: Begin CSI Store'),
    'E33': (r'^Scavenge: Completed, disposition: (.+?)$', 'Scavenge: Completed, disposition: <*>'),
    'E34': (r'^Scavenge: Starts$', 'Scavenge: Starts'),
    'E35': (r'^Session: (.+?)_(.+) initialized by client SPP\.$', 'Session: <*>_<*> initialized by client SPP.'),
    'E36': (r'^Session: (.+?)_(.+) initialized by client WindowsUpdateAgent\.$', 'Session: <*>_<*> initialized by client WindowsUpdateAgent.'),
    'E37': (r'^SQM: Cleaning up report files older than (.+?) days\.$', 'SQM: Cleaning up report files older than <*> days.'),
    'E38': (r'^SQM: Failed to start standard sample upload\. \[HRESULT = (.+?) - E_FAIL\]$', 'SQM: Failed to start standard sample upload. [HRESULT = <*> - E_FAIL]'),
    'E39': (r'^SQM: Failed to start upload with file pattern: (.+?), flags: (.+?) \[HRESULT = (.+?) - E_FAIL\]$', 'SQM: Failed to start upload with file pattern: <*>, flags: <*> [HRESULT = <*> - E_FAIL]'),
    'E40': (r'^SQM: Initializing online with Windows opt-in: False$', 'SQM: Initializing online with Windows opt-in: False'),
    'E41': (r'^SQM: Queued (.+?) file\(s\) for upload with pattern: (.+?), flags: (.+?)$', 'SQM: Queued <*> file(s) for upload with pattern: <*>, flags: <*>'),
    'E42': (r'^SQM: Requesting upload of all unsent reports\.$', 'SQM: Requesting upload of all unsent reports.'),
    'E43': (r'^SQM: Warning: Failed to upload all unsent reports\. \[HRESULT = (.+?) - E_FAIL\]$', 'SQM: Warning: Failed to upload all unsent reports. [HRESULT = <*> - E_FAIL]'),
    'E44': (r'^Starting the TrustedInstaller main loop\.$', 'Starting the TrustedInstaller main loop.'),
    'E45': (r'^Starting TrustedInstaller finalization\.$', 'Starting TrustedInstaller finalization.'),
    'E46': (r'^Starting TrustedInstaller initialization\.$', 'Starting TrustedInstaller initialization.'),
    'E47': (r'^Startup processing thread terminated normally$', 'Startup processing thread terminated normally'),
    'E48': (r'^TrustedInstaller service starts successfully\.$', 'TrustedInstaller service starts successfully.'),
    'E49': (r'^Unloading offline registry hive: (.+?)$', 'Unloading offline registry hive: <*>'),
    'E50': (r'^Warning: Unrecognized packageExtended attribute\.$', 'Warning: Unrecognized packageExtended attribute.'),
}

def classify_log(log_line):
    for event_id, (pattern, message) in event_patterns.items():
        match = re.match(pattern, log_line)
        if match:
            return event_id, match.groups(), message
    return 'E0', None, None  # Return E0 if no pattern matches

def parse_log_file(log_file):
    log_entries = []
    counter = 1  # Initialize counter
    
    with open(log_file, 'r', encoding='utf-8', errors='ignore') as file:
        log_data = file.readlines()
        
    pattern = r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}), (\w+)\s+(\w+)\s+(.*)'
    regex = re.compile(pattern)
    
    for line in log_data:
        match = regex.match(line.strip())
        if match:
            timestamp = match.group(1)
            level = match.group(2)
            component = match.group(3)
            event_template = match.group(4)  # Assume event template is the entire remaining part of the line
            parameters = None  # Depending on your actual log structure
            
            # Classify log based on pattern match
            event_id, groups, message = classify_log(event_template)
            if event_id:
                event_template = {
                    "EventId": event_id,
                    "EventPattern": pattern,
                    "Message": message.format(*groups) if message else None
                }
            
            log_entry = {
                "number": counter,  # Add the counter for each log entry
                "timestamp": timestamp,
                "level": level,
                "component": component,
                "event_template": event_template,
                "parameters": parameters
            }
            log_entries.append(log_entry)
            counter += 1  # Increment the counter
        else:
            print(f"Unmatched line: {line}")
    
    return log_entries


def save_to_json(log_entries, output_file):
    with open(output_file, 'w') as f:
        json.dump(log_entries, f, indent=4)


# Example usage:
if __name__ == "__main__":
    log_file = path
    output_file = 'parsed_logs.json'
    
    parsed_logs = parse_log_file(log_file)
    save_to_json(parsed_logs, output_file)
    print(f"Successfully parsed {len(parsed_logs)} entries. JSON saved to {output_file}")
