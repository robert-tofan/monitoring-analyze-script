from datetime import datetime, timedelta
from config import WARNING_THRESHOLD, ERROR_THRESHOLD, LOG_FILE_PATH, OUTPUT_FILE_PATH
import logging

# Function to parse a single log entry and split intems by commas
def parse_log_entry(line):
        
    try:
        parts = line.strip().split(',')
        # Check if the log line has exactly 4 parts: timestamp, description, status, job_id
        if len(parts) != 4:
            raise ValueError("Invalid log line: incorrect number of fields")
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
    except ValueError as e:
        # Log the error with a message indicating the line that caused the issue
        print(f"Error parsing line: {line.strip()} (Error: {e})")
        return None
    

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
                report.append(f"ERROR: Job {job_id} ({description}) took too long to complete above threshhold of 10 min: {duration_str}")
            elif duration > WARNING_THRESHOLD:
                report.append(f"WARNING: Job {job_id} ({description}) completed on low performance above threshhold of 5 min: {duration_str}")
        elif start_time and not end_time:
            # Job started but it's still running
            start_datetime = datetime.combine(today, start_time)
            elapsed = now - start_datetime
            if now < start_datetime:
                # If elapsed time is negative, it means the job started yesterday
                elapsed = now + timedelta(days=1) - start_datetime
            duration_seconds = elapsed.total_seconds()
            hours = int(duration_seconds // 3600)
            minutes = int((duration_seconds % 3600) // 60)
            seconds = int(duration_seconds % 60)
            duration_str = f"{hours}:{minutes:02d}:{seconds:02d}"
            # Check if the job duration exceeds thresholds
            if elapsed > ERROR_THRESHOLD:
                report.append(f"ERROR: Job {job_id} ({description}) is still running and exceeded 10 minutes: {duration_str}")
            elif elapsed > WARNING_THRESHOLD:
                report.append(f"WARNING: Job {job_id} ({description}) is still running and exceeded 5 minutes: {duration_str}")
        elif not start_time and end_time:
            # Job has an end time but no start time, which is logically inconsistent
            end_time_str = end_time.strftime('%H:%M:%S')
            report.append(f"ERROR: Job {job_id} ({description}) has an end time ({end_time_str}) without a start time")
            
    return report

def main():
    # Set up logging configuration
    try:
        with open(LOG_FILE_PATH, 'r') as file:
            logs_entries =[]
            # Read each line from the log file and parse it into structured entries
            # Skip empty lines to avoid parsing errors
            for line in file:
                if line.strip():
                    entry = parse_log_entry(line)
                    if entry:
                        logs_entries.append(entry)

        if not logs_entries:
            print("Log file is empty or contains no valid entries")
            return
        
        logging.basicConfig(filename=OUTPUT_FILE_PATH, level=logging.INFO, format='%(asctime)s: %(message)s', datefmt='%Y-%m-%d %H:%M')

        logs_report = analyze_logs(logs_entries)
        for message in logs_report:
            if message.startswith("ERROR"):
                logging.error(message)
            elif message.startswith("WARNING"):
                logging.warning(message)
    # Throw an error if the log file is not found or if there are parsing issues
    except FileNotFoundError:
        print(f"Log file {LOG_FILE_PATH} not found. Please ensure the file exists.")
    except Exception as e:
        print(f"An error occurred while processing the log file: {e}")
    


if __name__ == "__main__":
    main()
        