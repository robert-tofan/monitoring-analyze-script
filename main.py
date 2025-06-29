from datetime import datetime, timedelta
import logging

WARNING_THRESHOLD = timedelta(minutes=5)
ERROR_THRESHOLD = timedelta(minutes=10)

# Function to parse a single log entry and split intems by commas
def parse_log_entry(line):

    parts = line.strip().split(',')
    timestamp_str = parts[0].strip()
    timestamp = datetime.strptime(timestamp_str, '%H:%M:%S').time()
    description = parts[1].strip()
    status = parts[2].strip()
    job_id = parts[3].strip()
    return {
        'timestamp': timestamp,
        'description': description,
        'status': status,
        'job_id': job_id
    }
    

def analyze_logs(log_entries):
    jobs = {}
    report = []
    now = datetime.now()
    today = now.date()

    # Group log entries by job_id and record start/end times in jobs dictionary
    for entry in log_entries:
        job_id = entry['job_id']
        status = entry['status'].upper()
        description = entry['description']
        timestamp = entry['timestamp']
        if job_id not in jobs:
            jobs[job_id] = {'description': description}
        if status == 'START':
            jobs[job_id]['start_time'] = timestamp
        elif status == 'END':
            jobs[job_id]['end_time'] = timestamp

    # Iterate over each collected job to evaluate its duration and status
    for job_id, data in jobs.items():
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        description = data['description']
        if start_time and end_time:
            #Convert time to datetime for duration calculation
            start_datetime = datetime.combine(today, start_time)
            end_datetime = datetime.combine(today, end_time)
            if end_datetime < start_datetime:
                # If end time is earlier than start time, assume it was on the next day
                end_datetime += timedelta(days=1)
            duration = end_datetime - start_datetime
            # Transform duration to duration seconds and construct timedelta
            duration_seconds = duration.total_seconds()
            hours = int(duration_seconds // 3600)
            minutes = int((duration_seconds % 3600) // 60)
            seconds = int(duration_seconds % 60)
            duration_str = f"{hours}:{minutes:02d}:{seconds:02d}"
            # Check if the job duration exceeds thresholds
            if duration > ERROR_THRESHOLD:
                report.append(f"ERROR: Job {job_id} ({description}) took too long to complete above threshold of 10 min: {duration_str}")
            elif duration > WARNING_THRESHOLD:
                report.append(f"WARNING: Job {job_id} ({description}) took longer than expected above threshhold of 5 min: {duration_str}")
    return report

def main():
    # Prepare logging to file
    current_time = datetime.now().strftime('%Y%m%d%H%M')
    log_file_path = './logs.log'
    output_file_path = f"./output_logs/analysed_logs_{current_time}.log"
    # Set up logging configuration
    logging.basicConfig(filename=output_file_path, level=logging.INFO, format='%(message)s')
    with open(log_file_path, 'r') as file:
        logs_entries =[]
        # Read each line from the log file and parse it into structured entries
        # Skip empty lines to avoid parsing errors
        for line in file:
            if line.strip():
                entry = parse_log_entry(line)
                logs_entries.append(entry)

    logs_report = analyze_logs(logs_entries)
    for message in logs_report:
        if message.startswith("ERROR"):
            logging.error(message)
        elif message.startswith("WARNING"):
            logging.warning(message)

if __name__ == "__main__":
    main()
        