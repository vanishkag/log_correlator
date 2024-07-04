import re
import json
from typing import List, Dict

# Example log lines
log_lines = [
    "2016-09-28 04:30:30, Info                  CBS    Loaded Servicing Stack v6.1.7601.23505 with Core: C:\\Windows\\winsxs\\amd64_microsoft-windows-servicingstack_31bf3856ad364e35_6.1.7601.23505_none_681aa442f6fed7f0\\cbscore.dll",
    "2016-09-28 04:30:31, Info                  CBS    SQM: Warning: Failed to upload all unsent reports. [HRESULT = 0x80004005 - E_FAIL]"
]

# Regular expression to match the log line
log_pattern = re.compile(
    r"(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\s+"
    r"(?P<level>\w+)\s+"
    r"(?P<component>\w+)\s+"
    r"(?P<event_template>.+)"
)

# Patterns to identify parameters
params_patterns = [
    re.compile(r"\b(v\d+\.\d+\.\d+\.\d+)\b"),    # Version numbers
    re.compile(r"\b([A-Za-z]:\\[^ ]+)\b"),       # File paths
    re.compile(r"\[(HRESULT\s*=\s*0x[0-9A-Fa-f]+)\s*-\s*(\w+)\]") # HRESULT codes
]

def replace_params(event_template: str) -> (str, List[str]):
    parameters = []
    for pattern in params_patterns:
        matches = pattern.findall(event_template)
        if matches:
            for match in matches:
                if isinstance(match, tuple):
                    full_match = pattern.search(event_template).group(0)
                    event_template = event_template.replace(full_match, f"HRESULT = <*> - {match[1]}", 1)
                    parameters.append(match[0])
                else:
                    event_template = event_template.replace(match, "<*>", 1)
                    parameters.append(match)
    return event_template, parameters

def parse_log_line(line: str) -> Dict[str, str]:
    match = log_pattern.match(line)
    if match:
        log_components = match.groupdict()
        event_template = log_components["event_template"]
        event_template, parameters = replace_params(event_template)
        log_components["event_template"] = event_template.strip()
        log_components["parameters"] = parameters
        return log_components
    else:
        raise ValueError("Log line format is incorrect.")

# Parse the log lines
parsed_logs = [parse_log_line(line) for line in log_lines]

# Print the parsed logs
for log in parsed_logs:
    print(log)

# Store the parsed logs in a JSON file
with open('parsed_logs.json', 'w') as json_file:
    json.dump(parsed_logs, json_file, indent=4)

print("Parsed logs have been stored in 'parsed_logs.json'.")
