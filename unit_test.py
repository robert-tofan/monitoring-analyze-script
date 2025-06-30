import unittest
from datetime import datetime, timedelta
from analyze_log_script import parse_log_entry, analyze_logs, main
from unittest.mock import patch, mock_open
import io
import sys
import os

class TestLogMonitor(unittest.TestCase):
    # Test cases for the log monitoring script
    # Test the parse_log_entry function to ensure it correctly parses valid log entries
    def test_parse_valid_line(self):
        line = "12:00:30,test job,START,12345"
        result = parse_log_entry(line)
        self.assertIsNotNone(result)
        self.assertEqual(result['status'], "START")
        self.assertEqual(result['job_id'], "12345")
        self.assertEqual(result['timestamp'], datetime.strptime("12:00:30", "%H:%M:%S").time())

    # Test the parse_log_entry function to ensure it returns None for invalid log entries
    def test_parse_malformed_line(self):
        line = "12:00:30,missing field,START" 
        result = parse_log_entry(line)
        self.assertIsNone(result)

    # Test the parse_log_entry function to ensure it handles invalid timestamps gracefully
    def test_parse_invalid_timestamp(self):
        line = "27:80:99,test job,START,12345"
        result = parse_log_entry(line)
        self.assertIsNone(result)

    # Test the analyze_logs function with a normal job duration
    def test_job_normal_duration(self):
        entries = [
            {'timestamp': datetime.strptime("11:00:00","%H:%M:%S").time(), 'description': "job1", 'status': 'START', 'job_id': '1'},
            {'timestamp': datetime.strptime("11:04:59","%H:%M:%S").time(), 'description': "job1", 'status': 'END', 'job_id': '1'}
        ]
        report = analyze_logs(entries)
        self.assertEqual(report, [])

    # Test the analyze_logs function with a job that exceeds the warning threshold
    def test_job_warning_threshold(self):
        entries = [
            {'timestamp': datetime.strptime("10:00:00","%H:%M:%S").time(), 'description': "job2", 'status': 'START', 'job_id': '2'},
            {'timestamp': datetime.strptime("10:07:00","%H:%M:%S").time(), 'description': "job2", 'status': 'END', 'job_id': '2'}
        ]
        report = analyze_logs(entries)
        self.assertEqual(len(report), 1)
        self.assertIn("WARNING", report[0])
        self.assertIn("job2", report[0])
        self.assertIn("low performance", report[0])

    # Test the analyze_logs function with a job that exceeds the error threshold
    def test_job_error_threshold(self):
        entries = [
            {'timestamp': datetime.strptime("09:00:00","%H:%M:%S").time(), 'description': "job3", 'status': 'START', 'job_id': '3'},
            {'timestamp': datetime.strptime("09:11:00","%H:%M:%S").time(), 'description': "job3", 'status': 'END', 'job_id': '3'}
        ]
        report = analyze_logs(entries)
        self.assertEqual(len(report), 1)
        self.assertIn("ERROR", report[0])
        self.assertIn("job3", report[0])
        self.assertIn("took too long", report[0])
        self.assertIn("0:11:00", report[0])

    # Test the analyze_logs function with a job that has no end time
    def test_still_running_job(self):
        start_time = (datetime.now() - timedelta(minutes=11)).strftime("%H:%M:%S")
        entries = [{'timestamp': datetime.strptime(start_time,"%H:%M:%S").time(),
                    'description': "job4", 'status': 'START', 'job_id': '4'}]
        report = analyze_logs(entries)
        self.assertEqual(len(report), 1)
        self.assertIn("ERROR", report[0])
        self.assertIn("job4", report[0])
        self.assertIn("still running", report[0])
        self.assertIn("exceeded 10 minutes", report[0])

    # Test the analyze_logs function with an end entry without a corresponding start
    def test_end_without_start(self):
        entries = [{'timestamp': datetime.strptime("12:05:00","%H:%M:%S").time(),
                    'description': "job5", 'status': 'END', 'job_id': '5'}]
        report = analyze_logs(entries)
        self.assertEqual(len(report), 1)
        self.assertIn("ERROR", report[0])
        self.assertIn("job5", report[0])
        self.assertIn("without a start time", report[0])

    # Test the main function to ensure it handles file reading and writing correctly
    def test_missing_file_handled_gracefully(self):
        # Mock open to raise FileNotFoundError
        with patch('builtins.open', mock_open()) as mock_file:
            mock_file.side_effect = FileNotFoundError("File not found")
            
            # Capture stdout
            captured_output = io.StringIO()
            sys.stdout = captured_output
            
            # Call main() which should handle the FileNotFoundError
            main()
            
            sys.stdout = sys.__stdout__
            output = captured_output.getvalue()
            
            # Verify the error message was printed
            self.assertIn("logs_bad_entries.log not found", output)

if __name__ == '__main__':
    # Create output directory if it doesn't exist
    output_dir = 'unit_test'
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate timestamp for filename
    timestamp = datetime.now().strftime('%Y%m%d%H%M')
    output_file = os.path.join(output_dir, f'output_{timestamp}.log')
    
    # Run tests with file output
    with open(output_file, 'w') as f:
        runner = unittest.TextTestRunner(stream=f, verbosity=2)
        unittest.main(testRunner=runner, exit=False)
    
    print(f"Test results written to: {output_file}")