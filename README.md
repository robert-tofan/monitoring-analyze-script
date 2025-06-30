# Log Analyser App

A lightweight Python application designed to parse log files, analyze job durations, and report performance issues like long-running tasks or incomplete executions. Ideal for basic log inspection and performance diagnostics in time-tracked systems.

---

## Features

### Main App
- Parses logs with timestamp, description, status, and job ID
- Detects jobs that exceed duration thresholds (warnings/errors)
- Flags jobs still running with no end time
- Flags bad inputs log with no start but with end
- Generates a timestamped log report with all issues

#### Log File Format
The application expects log files in CSV format with the following structure:
- HH:MM:SS,job_description,STATUS,job_id

### Unit tests

- Comprehensive test suite covering all possible scenarios and behaviors
- Test cases include:
- Successful parsing and analysis
- Malformed log lines
- Invalid timestamps
- Empty file or missing log file scenarios
- Edge cases (jobs without start/end times)
- Performance threshold validation


### Configuration
The application uses configuration files for easy customization:
- config.py - Main application settings (file paths, thresholds)
- unittest_config.py - Unit test output settings

### Usage 
1. python analyze_log_script.py
2. python unit_test.py

### Output
- Analysis results: Stored in output_logs/ with timestamp
- Unit test results: Stored in unit_test/ with timestamp
---

## Project Structure

    monitoring_analyze_script/
    ├── analyze_log_script.py             # Main script that reads logs and generates report
    ├── config.py                         # Parameters for analyze_log_script.py
    ├── logs.log                          # Sample log file for testing 
    ├── output_logs/                      # Folder for storing output logs of analyze_log_script.py
    ├── unit_test.py                      # Unit tests for analyze_log_script.py
    ├── unittest_config.py                # Parameters for unit_test.py
    └── unit_test/                        # Folder for storing unit test results
