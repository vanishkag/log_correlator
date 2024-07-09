import re
import csv

# Define the log file and output CSV file paths
log_file_path = 'C:\Personal\log_correlator\Windows_2k.log'
output_csv_path = 'Windows_2k_structured_with_event_ids.csv'

# Regular expression pattern to match the log entries
log_pattern = re.compile(r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}), (?P<level>\w+)\s+(?P<source>\S+)\s+(?P<message>.*)')

# Function to generate an event template and parameters from a log message
def generate_event_template_and_parameters(message):
    # Replace dynamic parts of the message with placeholders
    template = re.sub(r'\d{4}-\d{2}-\d{2}', '<*>', message)
    template = re.sub(r'\d{2}:\d{2}:\d{2}', '<*>', template)
    template = re.sub(r'\d+', '<*>', template)
    template = re.sub(r'[A-Fa-f0-9]{8}', '<*>', template)
    
    # Extract parameters (parts of the message that match the placeholders)
    parameters = re.findall(r'\d{4}-\d{2}-\d{2}|\d{2}:\d{2}:\d{2}|\d+|[A-Fa-f0-9]{8}', message)
    
    return template, parameters

# Dictionary to store templates and their assigned event IDs
template_to_event_id = {}
event_id_counter = 1

# Open the log file and output CSV file
with open(log_file_path, 'r') as log_file, open(output_csv_path, 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    # Write the header row
    csv_writer.writerow(['Timestamp', 'Level', 'Source', 'Message', 'EventTemplate', 'Parameters', 'EventID'])
    
    # Iterate through each line in the log file
    for line in log_file:
        match = log_pattern.match(line)
        if match:
            # Extract the matched groups
            timestamp = match.group('timestamp')
            level = match.group('level')
            source = match.group('source')
            message = match.group('message')
            
            # Generate event template and parameters
            event_template, parameters = generate_event_template_and_parameters(message)
            
            # Assign an event ID to the template
            if event_template not in template_to_event_id:
                template_to_event_id[event_template] = event_id_counter
                event_id_counter += 1
            event_id = template_to_event_id[event_template]
            
            # Write the extracted data, event template, parameters, and event ID to the CSV file
            csv_writer.writerow([timestamp, level, source, message, event_template, ','.join(parameters), event_id])
