from datetime import datetime, timedelta

WARNING_THRESHOLD = timedelta(minutes=5)
ERROR_THRESHOLD = timedelta(minutes=10)
LOG_FILE_PATH = './logs.log'
CURRENT_TIME = datetime.now().strftime('%Y%m%d%H%M')
OUTPUT_FILE_PATH = f"./output_logs/analysed_logs_{CURRENT_TIME}.log"